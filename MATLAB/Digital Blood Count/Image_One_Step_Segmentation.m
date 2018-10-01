%#ok<*NASGU>
%#ok<*UNRCH>

clear 
clc
tic

% Acquire image
src = imread('Images/Latest.jpg');  % I put all images in the subfolder Images.
% src = imresize(src, [480 NaN]);  % Resize for fast operation.
src_original = src;
src(:,:,1) = zeros(size(src, 1), size(src, 2));

multiplierBrightness = 0.3;  % multiplier for the brightness threshold. default: 0.3
multiplierArea = 0.1; %.9;  % multiplier for the area threshold.
multiplierAreaCounter = 0.86;
multiplierDeletedCircle = 2;  % 1.45;
radiusDilation = 0;  % Minimum distance betwen pixels to be considered from same group (blob). defalut: 4
radiusErosion = 0;
grayLevels = 4;
dilation = false;
erosion = false;
holeFilling = true;
saveComponents = true;
drawAll = false;

imageGrayScale = rgb2gray(src);  % Convert to grayscale
imageGrayScaleEnhanced = histEqDiv(imageGrayScale, 1, 1, grayLevels); % histEqDiv(image, vertical division, horizontal division, gray levels 3) 

thresh = int8(multiplierBrightness*mean2(imageGrayScaleEnhanced));  % Get average brightness and set threshold
imageBinarySrc = imageGrayScaleEnhanced > thresh;  % Turn image to binary, set 0 each pixel with brightness less than thresh, 1 otherwise.

if dilation
    imageBinarySrcDilation = bwdist(~imageBinarySrc) <= radiusDilation;
    imageBinarySrcDilation = 255 * ~imageBinarySrcDilation;
    imageBinarySrc = imageBinarySrcDilation;
end

if holeFilling
    i = imfill(~imageBinarySrc,'holes');
    imageBinarySrcFilling = ~i;
    imageBinarySrc = imageBinarySrcFilling;
end

if erosion
    se = strel('disk', radiusErosion);
    im = imerode(~imageBinarySrc, se);
    imageBinarySrcErosion = ~im;
    imageBinarySrc = imageBinarySrcErosion;
end

% Detect and count WBC
imageBinary = imageBinarySrc == 0;
CC = bwconncomp(imageBinary);  % Get Connected Components (Blobs).
blobMap = labelmatrix(CC);  % give an index to each blob.
s = regionprops(blobMap, 'Area', 'Centroid', 'MajorAxisLength');  % Get the properties of all blobs.
threshArea = mean([s.Area]) * multiplierArea;  % Calculate area threshold.
threshArea = double(int32(threshArea));  % convert to proper type because matlab is being a baby about it.

imageBinary = bwareaopen(imageBinary, threshArea);  % Remove blobs that are smaller than threshArea

CC = bwconncomp(imageBinary);  % get blobs again now that we removed the smaller ones.
count = num2str(CC.NumObjects);
blobMap = labelmatrix(CC);
blobMap(imageBinarySrc) = 0;  % this is used to remove the swelling we used before, it sets index to zero, for pixels that are from the binary image background.
imageColoredBlobs = label2rgb(blobMap, 'hsv', 'k', 'shuffle');  % give different colors to each blob

s = regionprops(blobMap, 'Area', 'Centroid', 'MajorAxisLength', 'MinorAxisLength');  % Get the properties of all blobs.
centroids = cat(1, s.Centroid);
c = sum(size(centroids));

area = cat(1, s.Area);
diameters = cat(1, s.MajorAxisLength);
diametersMinor = cat(1, s.MajorAxisLength);
radiusMinor = min(diametersMinor);
radiusMinor = int8(radiusMinor/2);

countArea = sum(area)/(mean(area) * multiplierAreaCounter);
countArea = floor(countArea);

% Remove all counted Elements from image for next iteration.
tmp = zeros(size(imageBinary));

% Segmentated elements are saved one by one, to be analyzed in a later step.
count_RBC = 0;
count_WBC = 0;
count_Platelets = 0;
msg = [];

for j = 1 : str2double(count)
    xy = int16(centroids(j,:));
    x = xy(1);
    y = xy(2);
    hw = size(imageBinary);
    h = hw(1);
    w = hw(2);
    
    diameter = diameters(j);
    radius = multiplierDeletedCircle * diameter/2;
    maskCentroid = zeros(size(imageBinary));
    maskCentroid(y, x) = 1;    
    tmp = tmp + (bwdist(maskCentroid) <= radius);
    eleColored = src_original( max(y - radius, 1): min(y + radius, h), max(x - radius, 1): min(x + radius, w), :);
    eleBinary1 = blobMap == j ;
    eleBinary = eleBinary1( max(y - radius, 1): min(y + radius, h), max(x - radius, 1): min(x + radius, w));
    ele = uint8(eleBinary) .* eleColored;
    
    if diameter < 30    
        count_Platelets = count_Platelets + 1;
        msg = ['Images/Results/Platelets_', num2str(count_Platelets), '_', num2str(diameter), '.png'];
    
    elseif diameter < 120
        count_RBC = count_RBC + 1;
        msg = ['Images/Results/RBC_', num2str(count_RBC), '_', num2str(diameter), '.png'];    
        
    elseif  diameter >= 120 && diameter < 150
        elem = ele;
        M = repmat(all(~ele, 3), [1 1 3]);
        elem(M) = 255;

        elem = rgb2gray(elem);
        thr = mean2(elem);
        elem = elem > 0.2*thr;

        wbc = mean2(elem);
        
        if wbc == 1
            eleGrayScale = rgb2gray(ele);  % Convert to grayscale
            [centers, radii] = imfindcircles(ele, [25 60], 'Sensitivity', 0.97);
            s = size(centers);            
            
%             if s(1) > 1
%                 figure('Name', ['RBC_Bounded_: ', num2str(s(1))],'NumberTitle','off');
%                 imshow(ele)
%                 viscircles(centers, radii, 'EdgeColor', 'b');
%             end

            count_RBC = count_RBC + s(1);
            msg = ['Images/Results/RBC_Bounded_', num2str(count_RBC), '_', num2str(s(1)), '.png'];
        else
            count_WBC = count_WBC + 1;
            msg = ['Images/Results/WBC_', num2str(count_WBC), '_', num2str(diameter), '.png'];
            
        end       
        
    else    
        
        eleGrayScale = rgb2gray(ele);  % Convert to grayscale
        [centers, radii] = imfindcircles(ele, [25 60], 'Sensitivity', 0.97);
        s = size(centers);
        
        count_RBC = count_RBC + s(1);
        msg = ['Images/Results/RBC_Bounded_', num2str(count_RBC), '_', num2str(s(1)), '.png'];
    end
    
    if saveComponents
        imwrite(ele, msg, 'png');
    end
end

imageBinary = uint8(~tmp);
mask = cat(3, imageBinary, imageBinary, imageBinary);  % Create mask in an RGB format.
imageWithoutElements = src_original .* mask;  % multiplying element by element so the blobs are removed in each channel
M = repmat(all(~imageWithoutElements, 3), [1 1 3]);  % Turn all pure black pixel into white.
imageWithoutElements(M) = 255;

if drawAll
    figure('Name', 'Digital CBC','NumberTitle','off');  % Don't know the name.
    r1 = 2;
    c1 = 4;
    p1 = 1;
    
    p1 = addPlot(src_original, 'Original', r1, c1, p1);
    p1 = addPlot(imageGrayScale, 'Grayscale', r1, c1, p1);
    p1 = addPlot(imageGrayScaleEnhanced, 'Histogram Equalization', r1, c1, p1);
    p1 = addPlot(imageBinarySrc, ['Thresholding: ', num2str(thresh)], r1, c1, p1);
    
    if dilation
        p1 = addPlot(imageBinarySrcDilation, ['Dilation: ', num2str(radiusDilation)], r1, c1, p1);
    end
    
    if erosion 
        p1 = addPlot(imageBinarySrcErosion, ['Erosion: ', num2str(radiusErosion)], r1, c1, p1);
    end
    
    if holeFilling
        p1 = addPlot(imageBinarySrcFilling, 'Holes Filling', r1, c1, p1);
    end
    
    msg = compose(['Connected', '\n', ' Componnents: ', num2str(count), '/', num2str(countArea)]);
    p1 = addPlot(imageColoredBlobs, msg, r1, c1, p1);
%     p1 = addPlot(imageWithoutElements, 'Image Without Elements', r1, c1, p1);
end

% figure('Name', 'Elements Removed','NumberTitle','off');
% imshow(imageWithoutWBC);

% figure('Name', 'Colored Blobs','NumberTitle','off');
% imshow(imageColoredBlobs);

disp(['RBC: ', num2str(count_RBC)]);
disp(['WBC: ', num2str(count_WBC)]);
disp(['Platelets: ', num2str(count_Platelets)]);

toc


function src = histEqDiv(src, dw, dh, g)
    hw = size(src);
    h = hw(1);
    w = hw(2);
%     d = 8;

    for n = 0: dw    
        w1 = int32(w - (dw - n)*w/dw + 1);
        w2 = int32(min(w1 + w/dw, w));
%         src(:, w1:w2) = histeq(src(:, w1:w2), 3); % Improve contrast, n gray levels
        
        for j = 0: dh
            h1 = int32(h - (dh - j)*h/dh + 1);
            h2 = int32(min(h1 + h/dh, h));
            src(h1:h2, w1:w2) = histeq(src(h1:h2, w1:w2), g); % Improve contrast, n gray levels

        end
    end
    
end

function p_ = addPlot(image_, title_, m, n, p)
    subplot(m, n, p);
    imshow(image_);
    title(title_);
    p_ = p + 1;
end

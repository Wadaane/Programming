%#ok<*NASGU>
%#ok<*UNRCH>

clear 
clc
tic

% Acquire image
src = imread('Images/Latest.jpg');  % I put all images in the subfolder Images.
% RBC: 304
% WBC: 2
% Platelets: 35
src_original = src;

src(:,:,1) = 0.1 .* src(:,:,1);
src(:,:,2) = 1.5 .* src(:,:,2);
src(:,:,3) = 0.1 .* src(:,:,3);

multiplierBrightness = 0.3;  % 0.3 multiplier for the brightness threshold.
multiplierArea = 0.01; % 0.1 multiplier for the area threshold.
multiplierAreaCounter = 0.86;
multiplierDeletedCircle = 2;  % 1.45;
radiusDilation = 3;  % Minimum distance betwen pixels to be considered from same group (blob). defalut: 4
radiusErosion = 0;
grayLevels = 4;

dilation = true;
erosion = false;
holeFilling = true;
saveComponents = true;
drawAll = false;
drawBounded = false;

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
% imageBinaryDebug = imageBinary;
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
    eleColored = src_original( max(y - radius, 1): min(y + radius, h), max(x - radius, 1): min(x + radius, w), :);
    eleBinary1 = blobMap == j ;
    eleBinary = eleBinary1( max(y - radius, 1): min(y + radius, h), max(x - radius, 1): min(x + radius, w));
    ele = uint8(eleBinary) .* eleColored;
    
    if diameter < 30    
        count_Platelets = count_Platelets + 1;
        msg = ['Images/Results/Platelets_', num2str(count_Platelets), '_', num2str(diameter), '.png'];
    
    elseif diameter < 100
        count_RBC = count_RBC + 1;
        msg = ['Images/Results/RBC_', num2str(count_RBC), '_', num2str(diameter), '.png'];    
        
    elseif  diameter >= 100 && diameter < 165
        elem = ele;
        M = repmat(all(~ele, 3), [1 1 3]);
        elem(M) = 255;

        elem = rgb2gray(elem);
        thr = mean2(elem);
        elem = elem > 0.2*thr;

        rbc = mean2(elem);
        
        if rbc >= 0.990
            eleGrayScale = rgb2gray(ele);  % Convert to grayscale
            [centers, radii] = imfindcircles(ele, [38 53], 'Sensitivity', 0.9912);
            s = size(centers);
            
            valide = s(1);
            removed = zeros(1, s(1));
            for y1 = 1 : s(1) - 1
                if removed(y1) == 0
                    for y2 = y1+1 : s(1)
                        distance = sqrt((centers(y1,1) - centers(y2,1))^2 + (centers(y1,2) - centers(y2,2))^2);

                        if 0.9 * radii(y1) > distance && 0.9 * radii(y2) > distance
                            valide = valide - 1;
                            removed(y2) = 1;
                        end
                    end
                end
            end
            
            s(1) = valide;
            
            if s(1) > 1 && drawBounded
                figure('Name', ['RBC_Bounded_: ', num2str(s(1))],'NumberTitle','off');
                imshow(ele)
                viscircles(centers, radii, 'EdgeColor', 'b');
            end

            count_RBC = count_RBC + s(1);
            msg = ['Images/Results/RBC_Bounded_', num2str(count_RBC), '_', num2str(diameter), '_', num2str(s(1)), '.png'];
        else
            count_WBC = count_WBC + 1;
            msg = ['Images/Results/WBC_', num2str(count_WBC), '_', num2str(diameter), '.png'];
            
        end       
        
    else    
        
        eleGrayScale = rgb2gray(ele);  % Convert to grayscale
        [centers, radii] = imfindcircles(ele, [38 53], 'Sensitivity', 0.9912);
        s = size(centers);
        
        valide = s(1);
        removed = zeros(1, s(1));
        for y1 = 1 : s(1) - 1
            if removed(y1) == 0
                for y2 = y1+1 : s(1)
                    distance = sqrt((centers(y1,1) - centers(y2,1))^2 + (centers(y1,2) - centers(y2,2))^2);

                    if 0.9 * radii(y1) > distance && 0.9 * radii(y2) > distance
                        valide = valide - 1;
                        removed(y2) = 1;
                    end
                end
            end
        end
        
        s(1) = valide;
        
        if s(1) > 1  && drawBounded
                figure('Name', ['RBC_Bounded_: ', num2str(s(1))],'NumberTitle','off');
                imshow(ele)
                viscircles(centers, radii, 'EdgeColor', 'b');
        end
        
        count_RBC = count_RBC + s(1);
        msg = ['Images/Results/RBC_Bounded_', num2str(count_RBC), '_', num2str(diameter), '_',num2str(s(1)), '.png'];
    end
    
    if saveComponents
        imwrite(ele, msg, 'png');
    end
end

mask2 = rgb2gray(imageColoredBlobs);
mask2 = mask2 == 0;
mask2 = uint8(mask2);
red = src_original(:, :, 1);
green = src_original(:, :, 2);
blue = src_original(:, :, 3);

imageWithoutElements = cat(3, red .* mask2, green .* mask2, blue .* mask2);

% mask2 = mask2 == 0;
% mask2 = uint8(mask2);
% mask2 = 255.*mask2;
% blank = zeros(size(mask2));
% mask2 = cat(3, blank, blank, mask2);
% imageWithoutElements = imageWithoutElements + mask2;

if saveComponents
        imwrite(imageColoredBlobs, 'Images/Counted_elements.png', 'png');
        imwrite(imageWithoutElements, 'Images/Uncounted_elements.png', 'png');
%         imwrite(imageBinaryDebug, 'Images/imageBinaryDebug.png', 'png');
end

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

function s = openSerial() %#ok<DEFNU>
    ports = seriallist;

    if isempty(ports)
        disp('No Arduino Connected');
        return
    end

    comPort = ports(1);
    s = serial(comPort);
    set(s,'DataBits',8);
    set(s,'StopBits',1);
    set(s,'BaudRate',9600);
    set(s,'Parity','none');
    fopen(s);
end

function send(s, msg)%#ok<DEFNU>
    fprintf(s, [msg, '#']);
end

function msg = read(s)%#ok<DEFNU>
    msg = fscanf(s);
end

function closeSerial(s)%#ok<DEFNU>
    fclose(s);
    delete(s);
    clear s
end

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

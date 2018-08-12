clear 
% clc
tic

% Acquire image
src = imread('Images/Latest.jpg');  % I put all images in the subfolder Images.
% src = imresize(src, [480 NaN]);  % Resize for fast operation.

red = src(:,:,1); % Red channel
green = src(:,:,2); % Green channel
blue = src(:,:,3); % Blue channel
a = zeros(size(src, 1), size(src, 2));  % Black Empty pixels.
src = cat(3, a, green, blue);  % Red Channel is removed.

% S1.jpg Manual Counting: 6 WBC, 63 RBC, 1 Platelet.
% HEME001.jpg
% Sat Jun 23 15-21-42.jpg
% Mon Jun 18 14-42-04
% 20180701_003022
% Latest.jpg 
    % RBC 60 < radius < 115 px
    % WBC: 122 px < radius < 144 px

multiplierBrightness = 0.3;  % multiplier for the brightness threshold. default: 0.3
multiplierArea = 0.1; %.9;  % multiplier for the area threshold.
multiplierAreaCounter = 0.86;
multiplierDeletedCircle = 2;  % 1.45;
radiusDilation = 0;  % Minimum distance betwen pixels to be considered from same group (blob). defalut: 4
radiusErosion = 0;

figure('Name', 'Digital CBC','NumberTitle','off');  % Don't know the name.
r1 = 2;
c1 = 4;
p1 = 1;
p1 = addPlot(src, 'Original', r1, c1, p1);

imageGrayScale = rgb2gray(src);  % Convert to grayscale
p1 = addPlot(imageGrayScale, 'Grayscale', r1, c1, p1);

imageGrayScale = histEqDiv(imageGrayScale, 1, 1, 3); % histEqDiv(image, vertical division, horizontal division, gray levels 3) 
p1 = addPlot(imageGrayScale, 'Histogram Equalization', r1, c1, p1);

thresh = int8(multiplierBrightness*mean2(imageGrayScale));  % Get average brightness and set threshold
imageBinarySrc = imageGrayScale > thresh;  % Turn image to binary, set 0 each pixel with brightness less than thresh, 1 otherwise.
p1 =addPlot(imageBinarySrc, ['Thresholding: ', num2str(thresh)], r1, c1, p1);

imageBinarySrc = bwdist(~imageBinarySrc) <= radiusDilation;
imageBinarySrc = 255 * ~imageBinarySrc;
p1 = addPlot(imageBinarySrc, ['Dilation: ', num2str(radiusDilation)], r1, c1, p1);

% i = imfill(~imageBinarySrc,'holes');
% imageBinarySrc = ~i;
% p1 = addPlot(imageBinarySrc, 'Holes Filling', r1, c1, p1);

se = strel('disk', radiusErosion);
im = imerode(~imageBinarySrc, se);
imageBinarySrc = ~im;
p1 = addPlot(imageBinarySrc, ['Erosion: ', num2str(radiusErosion)], r1, c1, p1);

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
msg = compose(['Connected', '\n', ' Componnents: ', num2str(count), '/', num2str(countArea)]);
p1 = addPlot(imageColoredBlobs, msg, r1, c1, p1);
% imwrite(imageColoredBlobs,['Images/Results/', '0.png'],'png');

% Remove all counted Elements from image for next iteration.
tmp = zeros(size(imageBinary));

% Segmentated elements are saved one by one, to be analyzed in a later step.
for j = 1 : str2double(count)
    xy = int16(centroids(j,:));
    x = xy(1);
    y = xy(2);
    hw = size(imageBinary);
    h = hw(1);
    w = hw(2);
    
    radius = diameters(j)/2;
    b = int8(radius);  % Used as Maximum radius in imfindcircles
    a = max(int8(b * 0.01), 1);  % Used as Minimum radius in imfindcircles
    
    radius = multiplierDeletedCircle*radius;
    maskCentroid = zeros(size(imageBinary));
    maskCentroid(y, x) = 1;    
    tmp = tmp + (bwdist(maskCentroid) <= radius);
    eleColored = imageColoredBlobs( max(y - radius, 1): min(y + radius, h), max(x - radius, 1): min(x + radius, w), :);
    eleBinary1 = blobMap == j ;
    eleBinary = eleBinary1( max(y - radius, 1): min(y + radius, h), max(x - radius, 1): min(x + radius, w));
    ele = uint8(eleBinary) .* eleColored;
    
%     if radius < 60
%         imwrite(ele,['Images/Results/Platelets_', num2str(j),'.png'],'png');
%     elseif  radius > 115
%         imwrite(ele,['Images/Results/WBC_', num2str(j),'.png'],'png');
%     else
%         imwrite(ele,['Images/Results/RBC_', num2str(j),'.png'],'png');
%     end
%     
%     eleGrayScale = rgb2gray(ele);  % Convert to grayscale
%     [centers, radii] = imfindcircles(eleGrayScale, [a b]);
%     centerSize = size(centers);
%     if centerSize(1) > 1
%         figure('Name', ['WBC and Compounds: ', num2str(radius)],'NumberTitle','off');
%         imshow(ele)
%         viscircles(centers, radii, 'EdgeColor', 'b');
%         viscircles(centers, radii);
%     end  
      
%     imwrite(ele,['Images/Results/', num2str(j),'.png'],'png');
end

imageBinary = uint8(~tmp);
mask = cat(3, imageBinary, imageBinary, imageBinary);  % Create mask in an RGB format.
imageWithoutWBC = src .* mask;  % multiplying element by element so the blobs are removed in each channel
M = repmat(all(~imageWithoutWBC, 3), [1 1 3]);  % Turn all pure black pixel into white.
imageWithoutWBC(M) = 255;

figure('Name', 'Colored Blobs','NumberTitle','off');
imshow(imageColoredBlobs);

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

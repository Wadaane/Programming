clear 
% clc
tic

% Acquire image
src = imread('Images/S1.jpg');  % I put all images in the subfolder Images.
% src = imresize(src, [480 NaN]);
% S1.jpg Manual Counting: 6 WBC, 63 RBC, 1 Platelet.
% HEME001.jpg
% Sat Jun 23 15-21-42.jpg
% Mon Jun 18 14-42-04
% 20180701_003022


multiplierBrightness = 0.3;  % multiplier for the brightness threshold. default: 0.3
minRadius = 4;  % Minimum distance betwen pixels to be considered from same group (blob). defalut: 4
multiplierArea = 0.9;  % multiplier for the area threshold.
multiplierAreaCounter = 0.86;
multiplierDeletedCircle = 1.45;

% Do the counting
WBC = countElements(src, multiplierBrightness, minRadius, multiplierArea, multiplierAreaCounter, multiplierDeletedCircle);
RBC = countElements(WBC.imageWithoutWBC, multiplierBrightness * 3, minRadius*0, multiplierArea*0.5, multiplierAreaCounter, multiplierDeletedCircle);
Platelet = countElements(RBC.imageWithoutWBC, multiplierBrightness, minRadius*0, multiplierArea*0.5, multiplierAreaCounter, multiplierDeletedCircle);

% Do All the drawing Now
m = 4;  % Rows
n = 3;  % Columns
p = 1;  % Index (incremented at each subplot)

figure('Name', 'Digital CBC','NumberTitle','off');  % Don't know the name.

% p = addPlot(src, 'Original Image', m, n, p);
p = addPlot(src, 'Original', m, n, p);
p = addPlot(WBC.imageGrayScale, 'imageGrayScale', m, n, p);
p = addPlot(WBC.imageBinarySrc, 'imageBinarySrc', m, n, p);

p = addPlot(src .* WBC.imageBinary, ['WBC: ', WBC.count, '/', WBC.countArea], m, n, p);
p = addPlot(WBC.imageColoredBlobs, ['WBC: ', WBC.count, '/', WBC.countArea], m, n, p);
p = addPlot(255 * WBC.imageBinary, ['WBC: ', WBC.count, '/', WBC.countArea], m, n, p);

p = addPlot(src .* RBC.imageBinary, ['RBC: ', RBC.count, '/', RBC.countArea], m, n, p);
p = addPlot(RBC.imageColoredBlobs, ['RBC: ', RBC.count, '/', RBC.countArea], m, n, p);
p = addPlot(255 * RBC.imageBinary, ['RBC: ', RBC.count, '/', RBC.countArea], m, n, p);

p = addPlot(src .* Platelet.imageBinary, ['Platelet: ', Platelet.count, '/', Platelet.countArea], m, n, p);
p = addPlot(Platelet.imageColoredBlobs, ['Platelet: ', Platelet.count, '/', Platelet.countArea], m, n, p);
p = addPlot(255 * Platelet.imageBinary, ['Platelet: ', Platelet.count, '/', Platelet.countArea], m, n, p);

toc

function cont = countElements(src, multiplierBrightness, minRadius, multiplierArea, multiplierAreaCounter, multiplierDeletedCircle)

imageGrayScale = rgb2gray(src);  % Convert to grayscale

% imageGrayScale = histEqDiv(imageGrayScale, 8, 2, 3); % histEqDiv(image, vertical division, horizontal division, gray levels)

thresh = multiplierBrightness*mean2(imageGrayScale);  % Get average brightness and set threshold
imageBinarySrc = imageGrayScale > thresh;  % Turn image to binary, set 0 each pixel with brightness less than thresh, 1 otherwise.

% imageBinary = imageBinarySrc;
% Detect and count WBC
imageBinary = bwdist(~imageBinarySrc) <= minRadius;  % join pixels that are less than minRadius distance separating them, needed for WBC with multiple disconnected nuclei.
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
if c > 0
    area = cat(1, s.Area);
    diameters = cat(1, s.MajorAxisLength);

    countArea = sum(area)/(mean(area) * multiplierAreaCounter);
    countArea = floor(countArea);

    % Remove all counted Elements from image for next iteration.
    tmp = zeros(size(imageBinary));

    for j = 1 : str2double(count)
        xy = int16(centroids(j,:));
        x = xy(1);
        y = xy(2);
        radius = multiplierDeletedCircle*diameters(j)/2;
        maskCentroid = zeros(size(imageBinary));
        maskCentroid(y, x) = 1;    
        tmp = tmp + (bwdist(maskCentroid) <= radius);
    end
    imageBinary = uint8(~tmp);
    mask = cat(3, imageBinary, imageBinary, imageBinary);  % Create mask in an RGB format.
    imageWithoutWBC = src .* mask;  % multiplying element by element so the blobs are removed in each channel
    M = repmat(all(~imageWithoutWBC, 3), [1 1 3]);  % Turn all pure black pixel into white.
    imageWithoutWBC(M) = 255;

    %  All done, now return the resutlts.
    cont.imageColoredBlobs = imageColoredBlobs;
    cont.imageWithoutWBC = imageWithoutWBC;
    cont.count = count;
    cont.countArea = num2str(countArea);
    cont.imageBinary = imageBinary;
    cont.imageBinarySrc = imageBinarySrc;
    cont.imageGrayScale = imageGrayScale;
else
    cont.imageColoredBlobs = src;
    cont.imageWithoutWBC = src;
    cont.count = 0;
    cont.countArea = 0;
    cont.imageBinary = src;
    cont.imageBinarySrc = src;
    cont.imageGrayScale = src;
end

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

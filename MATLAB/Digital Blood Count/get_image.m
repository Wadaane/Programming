% s = open_serial();
% images = get_files('Images/Samples/*.jpg');
% get_images(s, images);

% MARIAM 60 pictures
% 29954         149        6264
% 
% Elapsed time is 800 seconds.

% rbc: 3.95 10^6 (29954)
% wbc: 10.3 10^3 (78)
% plt: 216 10^3 (1649)

% 3950000/29954 = 131.8689
% 10300/149 = 69.1275
% 216000/6264 = 34.4828

% EMAD1
% 30551         954          70
% 
% Elapsed time is 709.789255 seconds.

% rbc: 3.99 10^6
% wbc: 5.3 10^3
% plt: 118 10^3

% 3990000/30551 = 130.6013
% 5300/954 = 5.5556
% 118000/70 = 1685
 
% Mohamed
% 28083         114        1155
% 
% Elapsed time is 586.427982 seconds.

% rbc: 3.88 10^6
% wbc: 7.1 10^3
% plt: 497 10^3

% 3880000/28083 = 138.1619
% 7100/114 = 62.2807
% 497000/1155 = 430.3030

% tic
% clc

% global myapp
% myapp = Project_App;

function r = get_image()
    path = 'Images/Samples/';
    r = process_files(path);
    % disp(r)
    % toc
end

function n_files = get_files(cmd)
    files = ls(cmd);
    n_files = size(files);
    n_files = n_files(1);

    for i = 1 : n_files
        filename = deblank(files(i, :));
        n_files(i) = ['Images/Samples/', filename];
    end    
end

function delay(millis)
    T = timer('TimerFcn',@(~,~)disp(''),'StartDelay', millis/1000);
    start(T);
    wait(T);
end

function s = open_serial()
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

function send_serial(s, cmd)
    fprintf(s, [cmd, '#']);
    
%     msg = [];
%     while isempty(msg)
%         msg = fscanf(s);
%     end
end

function msg = read_serial(s)
    msg = fscanf(s);
end

function close_serial(s)
    fclose(s);
    delete(s);
    clear s
end

function get_images(mSerial, n_images)
    global myapp
    send_serial(mSerial, 'run')
    delay(5000)

    run = true;
    pos = 1;

    while run
        next = true;
    
        while next
            msg_arduino = read_serial(mSerial);
            msg_arduino = str2double(msg_arduino);
            
            if msg_arduino == pos && pos <= 70
                myapp.progress_text(['Get Images: ', num2str(pos)]);
                frame = n_images(pos);
                name = ['Images/Samples/', num2str(pos)', '.jpg'];
                imwrite(frame, name)
                delay(500);
                send_serial(mSerial, 'next');
                next = true;
                pos = pos + 1;
                
            elseif msg_arduino == -1 || pos > 70
                run = false;
                next = false;
            end
            
            delay(500)
        end
    end    
end

function results = process_files(path)
    files = ls([path, '*.jpg']);
    n_files = size(files);
    n_files = n_files(1);
    results = [0 0 0];
    global myapp
    for i = 1 : n_files
        myapp.progress_text(['Processing Image: ', num2str(i)]);
        filename = deblank(files(i, :));
        file_name = [path, filename];
        res = process_image(file_name);
%         disp(['File: ',num2str(i)])
%         disp(res)
        results = results + res;
    end
end

function results = process_image(file_name)
    warning('off', 'Images:initSize:adjustingMag');
    
    multiplierBrightness = 1.1;  % 1.1 multiplier for the brightness threshold.
    multiplierArea = 0.01; % 0.2 multiplier for the area threshold.
    multiplierAreaCounter = 0.86;
    multiplierDeletedCircle = 2;  % 2;
    radiusDilation = 3;  % Minimum distance betwen pixels to be considered from same group (blob). defalut: 4
    radiusErosion = 3;
    grayLevels = 4;
    fcradiusmin = 30;
    fcradiusmax = 60;
    fcsensitivity = 0.95;

    dilation = false;
    erosion = false;
    holeFilling = true;
    
    saveComponents = false;
    
    drawAll = false;
    drawBigEle = false;
    drawBounded = false;

    % Acquire image
    src = imread(file_name);
    src(end, :, :) = 255;
    src_original = src;

    imageGrayScale = rgb2gray(src);  % Convert to grayscale    
    imageGrayScaleEnhancedImadj = imadjust(imageGrayScale, stretchlim(imageGrayScale));
    imageGrayScaleEnhanced = imageGrayScaleEnhancedImadj;
    
    thresh = multiplierBrightness*mean2(imageGrayScaleEnhanced);  % Get average brightness and set threshold
    imageBinarySrc = imageGrayScaleEnhanced > thresh;  % Turn image to binary, set 0 each pixel with brightness less than thresh, 1 otherwise.
    imageBinaryThresh = imageBinarySrc;

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

    s = regionprops(blobMap, 'Centroid', 'MajorAxisLength');  % Get the properties of all blobs.
    
    centroids = cat(1, s.Centroid);
    diameters = cat(1, s.MajorAxisLength);

    % Segmentated elements are saved one by one, to be analyzed in a later step.
    count_RBC = 0;
    count_WBC = 0;
    count_Platelets = 0;
    msg = [];
    
    Only_Platelets = imageBinary * 0;
    Only_RBC = Only_Platelets;
    Only_WBC = Only_Platelets;
%     
%     figure
%     imshow(src_original); 
%     title('Original');
% 
%     figure
%     imshow(imageGrayScale); 
%     title('Grayscale');
%  
%     figure
%     imshow(imageGrayScaleEnhancedImadj); 
%     title('Grayscale imadjust');
%     
%     figure
%     imshow(imageBinaryThresh); 
%     title('Binary');
% 
%     if dilation
%         figure
%         imshow(imageBinarySrcDilation);
%         title('Dilation');
%     end
%     
%     if holeFilling
%         figure
%         imshow(imageBinarySrcFilling);
%         title('Holes Filling');
%     end
%     
%     if erosion 
%         figure
%         imshow(imageBinarySrcErosion);
%         title('Erosion');
%     end

    
    for j = 1 : str2double(count)
        xy = int16(centroids(j,:));
        x = xy(1);
        y = xy(2);
        hw = size(imageBinary);
        h = hw(1);
        w = hw(2);

        diameter = diameters(j);
        radius = multiplierDeletedCircle * diameter/2;
        
        ele1 = imageGrayScaleEnhanced( max(y - radius, 1): min(y + radius, h), max(x - radius, 1): min(x + radius, w), :);
        eleBinary11 = blobMap == j ;
        eleBinary111 = eleBinary11( max(y - radius, 1): min(y + radius, h), max(x - radius, 1): min(x + radius, w));
        ele2 = uint8(eleBinary111) .* ele1 + uint8(245 * ~eleBinary111);
        size1 = size(ele2);
        
        xmin = 1;
        for xmin1 = 1 : size1(2)
            sum1 = sum(eleBinary111(:, xmin1));
            
            if sum1 > 0
                xmin = xmin1;
                break
            end                
        end           
        
        xmax = size1(2);
        for xmax1 = size1(2): -1: 1
            sum1 = sum(eleBinary111(:, xmax1));
            
            if sum1 > 0
                xmax = xmax1;
                break
            end                
        end           
        
        ymin = 1;
        for ymin1 = 1 : size1(1)
            sum1 = sum(eleBinary111(ymin1, :));
            
            if sum1 > 0
                ymin = ymin1;
                break
            end                
        end           
        
        ymax = size1(1);
        for ymax1 = size1(1): -1: 1
            sum1 = sum(eleBinary111(ymax1, :));
            
            if sum1 > 0
                ymax = ymax1;
                break
            end                
        end           
        
        ele2 = ele2(ymin:ymax, xmin:xmax);
        ele1 = ele1(ymin:ymax, xmin:xmax);
        ele = ele2;

        if diameter < 50    
            count_Platelets = count_Platelets + 1;
            msg = ['Images/Results/Platelets_', num2str(diameter), '_', num2str(count_Platelets), '.png'];
            Only_Platelets = Only_Platelets + eleBinary11;

        elseif diameter < 120
            count_RBC = count_RBC + 1;
            msg = ['Images/Results/RBC_', num2str(diameter), '_', num2str(count_RBC), '.png'];    
            Only_RBC = Only_RBC + eleBinary11;

        elseif  diameter >= 120  && diameter < 165
            elem = ele;
            thr = mean2(elem);
            elem = elem > 0.05*thr;

            rbc = mean2(elem);
            if rbc >= 0.8
                eleinv = ele < 0.75*mean2(ele);
                [centers, radii] = imfindcircles(eleinv, [fcradiusmin fcradiusmax], 'Sensitivity', fcsensitivity);
                s = size(centers);

                valide = s(1);
                removed = zeros(1, s(1));
                for y1 = 1 : s(1) - 1
                    if removed(y1) == 0
                        for y2 = y1+1 : s(1)
                            distance = sqrt((centers(y1,1) - centers(y2,1))^2 + (centers(y1,2) - centers(y2,2))^2);

                            if 1.5 * radii(y1) > distance && 1.5 * radii(y2) > distance
                                valide = valide - 1;
                                removed(y2) = 1;
                            end
                        end
                    end
                end

                valids = removed == 0;
                v_radii = radii(valids);
                v_centers = centers(valids, :);
                valide = sum(sum(valids));
                s(1) = sum(sum(valide));

                if s(1) > 1 && drawBounded
                    figure
                    imshow(ele)
                    title(['RBC Bounded: ', num2str(s(1))])
                    viscircles(v_centers, v_radii, 'EdgeColor', 'b');
                                       
                end

                Only_RBC = Only_RBC + eleBinary11;
                count_RBC = count_RBC + s(1);
                msg = ['Images/Results/RBC_Bounded_', num2str(diameter), '_',num2str(count_RBC), '_', num2str(s(1)), '.png'];
            else
                Only_WBC = Only_WBC + eleBinary11;
                count_WBC = count_WBC + 1;
                msg = ['Images/Results/WBC_', num2str(diameter), '_', num2str(count_WBC), '.png'];

            end       

        else
            eleinv = ele < 0.75*mean2(ele);
            [centers, radii] = imfindcircles(eleinv, [fcradiusmin fcradiusmax], 'Sensitivity', fcsensitivity);
            s = size(centers);            

            valide = s(1);
            removed = zeros(1, s(1));
            for y1 = 1 : s(1) - 1
                if removed(y1) == 0
                    for y2 = y1+1 : s(1)
                        distance = sqrt((centers(y1,1) - centers(y2,1))^2 + (centers(y1,2) - centers(y2,2))^2);

                        if 1.5 * radii(y1) > distance && 1.5 * radii(y2) > distance
                            valide = valide - 1;
                            removed(y2) = 1;
                        end
                    end
                end
            end
            
            valids = removed == 0;
            v_radii = radii(valids);
            v_centers = centers(valids, :);
    
            valide = sum(sum(valids));
            s(1) = sum(sum(valide));
            
            thr = mean2(ele);
            ele1 = ele1 > 0.3*thr;
            
            i = imfill(~ele1,'holes');
            ele1 = ~i;
            
            se = strel('disk', 7);
            im = imerode(~ele1, se);
            ele1 = ~im;    
            
            bw = ele1(:,:) == 0;
            bw = bwareaopen(bw, 5000);            

            area = sum(sum(bw));
            wbc1 = 0;
            
            if area > 5000 && area < 8000
                wbc1 = 1;
            elseif area > 8000
                wbc1 = area / 8000;
                wbc1 = int16(wbc1);
            end


            if drawBigEle
                figure
                imshow(ele2)
                title(['RBC: ', num2str(valide), ' WBC: ', num2str(wbc1)])
                if s(1) > 1  && drawBounded
                    viscircles(v_centers, v_radii, 'EdgeColor', 'b');
                end
            end
            
            yi = max(y - radius, 1) + ymin - 1;
            yf = yi + size(bw, 1) - 1;
            
            xi = max(x - radius, 1) + xmin - 1;
            xf = xi + size(bw, 2) - 1;
            
            Only_RBC = Only_RBC + eleBinary11;
            Only_RBC(yi : yf, xi : xf) = Only_RBC(yi : yf, xi : xf) .* ~bw;
            Only_WBC(yi : yf, xi : xf) = bw;
            
            count_RBC = count_RBC + s(1);
            count_WBC = count_WBC + wbc1;
            msg = ['Images/Results/WBC_RBC_Bounded_', num2str(diameter), '_',num2str(count_RBC), '_', num2str(wbc1), '_',num2str(s(1)), '.png'];
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

    if saveComponents
            imwrite(imageColoredBlobs, 'Images/Counted_elements.png', 'png');
            imwrite(imageWithoutElements, 'Images/Uncounted_elements.png', 'png');
    end

    if drawAll
        figure
        imshow(imageColoredBlobs)
        title('Connected Componnents');
        
        counted = cat(3, Only_Platelets, Only_RBC, Only_WBC);
        figure
        imshow(counted)
        title(['RBC (green): ', num2str(count_RBC), ' WBC (Blue): ', num2str(count_WBC), ' Platelets (Red): ', num2str(count_Platelets)]);        
    
    end
    
    results = zeros(1, 3, 'double');
    results(1) = count_RBC;
    results(2) = count_WBC;
    results(3) = count_Platelets;

end
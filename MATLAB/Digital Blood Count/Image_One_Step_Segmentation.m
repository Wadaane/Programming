%#ok<*NASGU>
%#ok<*UNRCH>

clear 
clc

mSerial = open_serial();

% Get Images and save them in folder
disp('Start taking pictures')
get_images(mSerial)
disp('Done taking pictures')
close_serial(mSerial);

% Process each file and store results
disp('Start Processing')
results = process_files();
disp(results)


function get_images(mSerial)
    vid = videoinput('winvideo', 2, 'MJPG_2592x1944');
    src = getselectedsource(vid);
    src.Contrast = 65;
    src.Brightness = 64;

    frame = getsnapshot(vid);
    send_serial(mSerial, 'run')
    delay(5000)

    run = true;
    pos = 1;

    while run
        next = true;
        entropy_prev = 0;
        choice = true;
        adjustment = ['inc'; 'dec'];
        tries = 1;
        
        t = tries;

        while next
            msg_arduino = read_serial(mSerial);
            msg_arduino = str2double(msg_arduino);
            
            if msg_arduino == pos || t < 1
                frame = getsnapshot(vid);
                ent = entropy(frame);
                if ent <= 6.5 || t == 0
                    name = ['Images/Samples/', num2str(pos), '_', num2str(ent), '.jpg'];
                    imwrite(frame, name)
                    delay(500);
                    send_serial(mSerial, 'next');
                    next = true;
                    pos = pos + 1;
                    t = tries;
                else
                    choice = xor(choice, entropy_prev <= ent);
                    send_serial(mSerial, adjustment(choice + 1, :));
                    entropy_prev = ent;
                    t = t - 1;
                end
            elseif msg_arduino == -1
                run = false;
                next = false;
            end
            
            delay(500)
        end
    end
    
    delete(vid);
end

function results = process_files()
    files = ls('Images/Samples/*.jpg');
    n_files = size(files);
    n_files = n_files(1);
    results = [0 0 0];

    for i = 1 : n_files
        filename = deblank(files(i, :));
        file_name = ['Images/Samples/', filename];
        res = process_image(file_name);
        disp(res)
        results = results + res;
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
    set(s,'Timeout',30);
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
    msg = [];
%     while isempty(msg)
        msg = fscanf(s);
%     end
end

function close_serial(s)
    fclose(s);
    delete(s);
    clear s
end

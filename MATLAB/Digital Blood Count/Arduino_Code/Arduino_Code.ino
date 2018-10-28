#define stepPinX 7
#define dirPinX 30
#define stepPinY 6
#define dirPinY 31
#define stepPinZ 5
#define dirPinZ 53
#define MS1 50
#define MS2 51
#define MS3 52



int stepPin = 0, dirPin = 0, jumps = 500, speedDelay = 500, microstepDivider = 4,
position_currentX = 0, position_currentY = 0, position_currentZ = 0,
z_max = 30, z_min = -10;
boolean start = false;

void rotate_steps(String cmd) {
	char axis = cmd.charAt(0);
	int steps = cmd.substring(1).toInt();
	int current = 0;
	String msg = "";

  // Select the right pins for the given axis.
  switch (axis) {
  	case 's':      
  	setMicrostepping(steps);
  	return;

  	case 'x':
  	dirPin = dirPinX;
  	stepPin = stepPinX;
  	jumps = 500;
  	speedDelay = 500;
  	current = position_currentX * jumps;
  	position_currentX = steps;
  	msg = 'x' + String(position_currentX);

  	break;
  	case 'y':
  	dirPin = dirPinY;
  	stepPin = stepPinY;
  	jumps = 100;
  	speedDelay = 500;
  	current = position_currentY * jumps;
  	position_currentY = steps;
  	msg = 'y' + String(position_currentY);

  	break;
  	case 'z':
  	dirPin = dirPinZ;
  	stepPin = stepPinZ;
  	jumps = 500;
  	speedDelay = 500;
  	current = position_currentZ * jumps;
  	steps *= -1;
  	position_currentZ = steps;
  	msg = 'z' + String(position_currentZ);

  	break;

  	default:
  	return;
  }

  int next = steps * jumps;
  steps = current - next;
  boolean dir = steps < 0;

	digitalWrite(dirPin, dir);  // If steps is positive direction is positive.
	steps = abs(steps);

	for (int i = 0; i < steps; i++) {
		digitalWrite(stepPin, HIGH);
		delayMicroseconds(speedDelay);
		digitalWrite(stepPin, LOW);
		delayMicroseconds(speedDelay);
	}
}

void setMicrostepping(int divider) {
	switch (divider) {
		case 1:
		digitalWrite(MS1, LOW);
		digitalWrite(MS2, LOW);
		digitalWrite(MS3, LOW);
		break;

		case 2:
		digitalWrite(MS1, HIGH);
		digitalWrite(MS2, LOW);
		digitalWrite(MS3, LOW);
		break;

		case 4:
		digitalWrite(MS1, LOW);
		digitalWrite(MS2, HIGH);
		digitalWrite(MS3, LOW);
		break;

		case 8:
		digitalWrite(MS1, HIGH);
		digitalWrite(MS2, HIGH);
		digitalWrite(MS3, LOW);
		break;

		case 16:
		digitalWrite(MS1, HIGH);
		digitalWrite(MS2, HIGH);
		digitalWrite(MS3, HIGH);
		break;
		
		default:
		digitalWrite(MS1, HIGH);
		digitalWrite(MS2, HIGH);
		digitalWrite(MS3, HIGH);
		break;
	}
}

int wait_check(int pos){
	delay(500);
	pos++;
	Serial.print(String(pos));

	boolean _next = false;
	while(!_next){
		if(Serial.available()){
			String status = Serial.readStringUntil('#');
			_next = status == "next";
			if(!_next){
				int value = 0;
				if(status == "inc")
					value = -5;
				else if(status == "dec")
				 	value = 5;
				
				value += position_currentZ;
				if(value < z_max) value = z_max;
				if(value > z_min) value = z_min;

				rotate_steps('z' + String(value));
			}
		}
	}

	return pos;
}

void run(){
	digitalWrite(LED_BUILTIN, HIGH);

	int pos = 0;
	rotate_steps('z' + String(25));
	
	for (int x = 0; x <= 20; x += 10) {
		rotate_steps('x' + String(x));
		pos = wait_check(pos);
	}

	rotate_steps('y' + String(30));
	
	for (int x = 20; x >= 0; x -= 10) {
		rotate_steps('x' + String(x));
		pos = wait_check(pos);
	}
	
	rotate_steps('y' + String(60));
	
	for (int x = 0; x <= 20; x += 10) {
		rotate_steps('x' + String(x));
		pos = wait_check(pos);
	}
	
	Serial.print("-1");
	rotate_steps('x' + String(0));
	rotate_steps('y' + String(0));
	rotate_steps('z' + String(0));
	
	digitalWrite(LED_BUILTIN, LOW);    
}

void setup() {
	Serial.begin(9600);

	pinMode(stepPinX, OUTPUT);
	pinMode(dirPinX, OUTPUT);
	pinMode(stepPinY, OUTPUT);
	pinMode(dirPinY, OUTPUT);
	pinMode(stepPinZ, OUTPUT);
	pinMode(dirPinZ, OUTPUT);
	pinMode(MS1, OUTPUT);
	pinMode(MS2, OUTPUT);
	pinMode(MS3, OUTPUT);

	setMicrostepping(microstepDivider);

	pinMode(LED_BUILTIN, OUTPUT);
	digitalWrite(LED_BUILTIN, start);
}

void loop() {
	while (Serial.available()) {
	String cmd = Serial.readStringUntil('#');  // Read given Axis and Steps in Serial.

	if (cmd == "start") {
		start = !start;
		digitalWrite(LED_BUILTIN, start);

		} else if (cmd == "run"){
			run();
			} else if (start) {
				rotate_steps(cmd);
			}
		}
}


#define stepPinX 7
#define dirPinX 30
#define stepPinY 6
#define dirPinY 31
#define stepPinZ 5
#define dirPinZ 53
#define MS1 52
#define MS2 51
#define MS3 50
    // MS1, MS2 and MS3 are used to set the microsteps.
    // stepPinX is for the step pulse
    // dirPinX is for the direction of rotation

int speedDelay = 500;  // The delay will set the speed of the movements.
int microstepDivider = 16;  // 1/16th step

int stepPin = 0, dirPin = 0;
boolean start = false;


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
}


void loop() {
  while (Serial.available()) {
    String cmd = Serial.readStringUntil('#');  // Read given Axis and Steps in Serial.

    if(start){        
        rotate_steps(cmd); 
        delay(speedDelay*2); // simple delay but not necessary.
    } else if(cmd == "start") {
        start != start;
    }
  }
}


void rotate_steps(String cmd) {
  char axis = cmd.charAt(0);
  int steps = cmd.substring(1).toInt();

  // Select the right pins for the given axis.
  switch (axis) {
    case 'x':
      dirPin = dirPinX;
      stepPin = stepPinX;
      break;
    case 'y':
      dirPin = dirPinY;
      stepPin = stepPinY;
      break;
    case 'z':
      dirPin = dirPinZ;
      stepPin = stepPinZ;
      break;

    default:
      return;
  }

  digitalWrite(dirPin, steps > 0);  // If steps is positive direction is positive.
  steps = abs(steps); // we need positive number of steps, so we take absolute value.

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
  }
}

#include <Servo.h>

#define pin_servo 3
#define pin_fan 5
#define pin_heater 6
#define pin_light 7
#define pin_alarm 8

Servo window;
String command = "";

void setup() {
  Serial.begin(9600);
  window.attach(pin_servo, 470, 2260);

  pinMode(pin_fan, OUTPUT);
  pinMode(pin_heater, OUTPUT);
  pinMode(pin_light, OUTPUT);
  pinMode(pin_alarm, OUTPUT);


}

void loop() {
  while(Serial.available()){
    command = Serial.readString();
    char c = command.charAt(0);
    command = command.substring(1);

    switch (c) {
        case 'w':
          handle_window(command);
          break;

        case 'f':
          handle_fan(command);
          break;

          case 'h':
          handle_heater(command);
          break;

          case 'l':
          handle_light(command);
          break;

          case 'a':
          handle_alarm(command);
          break;

        default:
          break;
    }
  }  
}

void handle_window(String command){
  int angle = command.toInt();
  angle = map(angle, 0, 100, 470, 2260);
  window.writeMicroseconds(angle);
}

void handle_fan(String command){
  int value = (command == "ON" ? HIGH: LOW);
  digitalWrite(pin_fan, value); 
}

void handle_heater(String command){
  int value = (command == "ON" ? HIGH: LOW);
  digitalWrite(pin_heater, value);  
}

void handle_light(String command){
  int value = (command == "ON" ? HIGH: LOW);
  digitalWrite(pin_light, value);
}

void handle_alarm(String command){
  int value = (command == "ON" ? HIGH: LOW);
  digitalWrite(pin_alarm, value);
}

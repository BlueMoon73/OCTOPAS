#include <SoftwareSerial.h>
#include <Servo.h>
Servo DispenserServo;

char input; 
int pos = 0;
SoftwareSerial BT(3, 2);

void setup() {
  DispenserServo.attach(9); 
Serial.begin(9600); 
BT.begin(9600); 
Serial.println("The bluetooth gates are open.\n Connect to HC-05 from any other bluetooth device with 1234 as pairing key!.");
//  DispenserServo.write(180);
//  delay(1000); 
//  DispenserServo.write(0);
  }

void loop() { 

   input = BT.read();  
    
    if (input == 'A'){
//        pos = 0;
//        Serial.println("It's A"); 
//        Serial.println(pos); 
//        DispenserServo.write(pos);
//        delay(1500); 
//        pos = 180; 
//        Serial.println(pos); 
//        DispenserServo.write(pos);
//        delay(1500);
      if (pos == 0) {
        pos = 180; 
//        delay(1500); 
        Serial.println(pos); 
        DispenserServo.write(pos);
        delay(1500); 
      }
      else if (pos == 180) {
        pos = 0; 
//          delay(1500); 
        Serial.println(pos); 
        DispenserServo.write(pos);
        delay(1500); 
      }
    }
  // put your main code here, to run repeatedly:

}

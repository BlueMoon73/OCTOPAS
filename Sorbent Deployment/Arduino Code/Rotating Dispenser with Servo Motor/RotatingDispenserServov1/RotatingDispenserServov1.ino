#include <SoftwareSerial.h>
#include <Servo.h>
Servo DispenserServo;

String inputString = ""; 
char input; 
int pos = 0;
int inputInt;
int timeMillis;
SoftwareSerial BT(3, 2);

void setup() {
  DispenserServo.attach(9); 
  Serial.begin(9600); 
  BT.begin(9600); 
  Serial.println("The bluetooth gates are open.\n Connect to HC-05 from any other bluetooth device with 1234 as pairing key!.");
}

void loop() { 
//    Serial.println(BT.available());    
    while (BT.available()) {
        delay(100);  //small delay to allow input buffer to fill
        input = BT.read();   //gets one byte from serial buffer]
        Serial.println("input read sucessfully" + input); 
        if (isDigit(input)){
                Serial.println("read the number: " + input);
                inputString.concat(input);
    }
        else {
          Serial.println("The character is not a number" + input);
             } 
          }  

    if (inputString.length() > 0) {

      if (inputString == 0){
        pos = 0; 
        DispenserServo.write(pos);
        timeMillis = 0; 
      }
      else { 
      
       Serial.println("the time is " + inputString); //prints string to serial port out
    
        inputInt = inputString.toInt();
        inputString="";
        Serial.println("the num of seconds to turn is: " + inputString); 

     if (inputInt > 0){
    
      turnServo(inputInt, DispenserServo);   
    }
    }
    }
    }
    
   

void  turnServo (int timeSec, Servo servo) {
    timeMillis = (timeSec * 1000); 
    Serial.println("the time in millis is " + String(timeMillis)); 
    pos = 180; 
    servo.write(pos);
    delay (timeMillis); 
    returnServo(servo); 
  
}

void returnServo (Servo servo){
  servo.write(0); 
  pos = 0;
  delay(1000);  
}

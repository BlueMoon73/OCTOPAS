
/* 
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
#
#  Author:  Monish Saravana Kumar Divya Sundari
#
#  Initial Date:  9/10/2022
#
#  Last Updated:  12/20/2022
#
#  Description:  The main python source code, for the OCTOPAS Algorithm, as found on
#                 https://github.com/BlueMoon73/OCTOPAS. OCTOPAS stands for Oil spill Cleanup Through an Optimized
#                 Pragmatic Automated System. OCTOPAS is a novel system aimed towards automating oil spill clean-ups.
#                 This is part of a # multi-year (currently year 3) research project, towards improving oil spill
#                 clean-ups.
#
#                ***Code was made for an Arduino Nano, MG996R Servo, and an HC-05 Bluetooth Module. 
#
#  Version: OCTOPAS 1.0
#
#  
#
#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
*/ 


// importing libraries 
// #include <SoftwareSerial.h> - to be able work with the HC-05 Bluetooth module, which lets the arduino send and recieve bluetooth signals 
// #include <Servo.h> - to be able to rotate the attached MG996R  servo

#include <SoftwareSerial.h>
#include <Servo.h>

// declares a servo object 
Servo DispenserServo;


// declares global variables to be sued later in the code 
  
String inputString = ""; 
char input; 
int pos = 0;
int inputInt;
int timeMillis;
unsigned long timeNow = 0;
SoftwareSerial BT(3, 2);


// Setup code to be run everytime the arduino is initialized 
void setup() {
  //"attaches" the servo to the arduino to be run on 
  DispenserServo.attach(9); 

  // returns the servo to the starting position 
  returnServo(DispenserServo); 

  // sets the baud rate of 9600 for the serial and bluetooth 
  Serial.begin(9600); 
  BT.begin(9600); 

  // prints to serial that bluetooth gates are open (debugging purpose) 
  Serial.println("The bluetooth gates are open");
}


void loop() { 
// while there is a message available to be raed 
    while (BT.available()) {
        //small delay to allow input buffer to fill
        delay(100); 

        //gets one byte from serial buffer
        input = BT.read();   

        // prints the read byte (for debugging) 
        Serial.println("input read sucessfully" + input); 

        // checks if the input byte was a numeric character 
        if (isDigit(input)){ 
          
                // prints the number that was read (for debugging) 
                Serial.println("read the number: " + input); 

                // concatenates the byte to the inputString
                inputString.concat(input);
    }
        // if the input byte is NOT a number, print the error message to the console 
        else {
          Serial.println("The character is not a number" + input);
             } 
          }  

    // if the inputString is NOT empty 
    if (inputString.length() > 0) {


      // if the inputString is equal to "0"  return the servo to base position 
      if (inputString == "0"){
        returnServo(DispenserServo);
      }

      // if the inputString is not equal to 0 
      else { 

        //prints string to serial port out
        Serial.println("the time is " + inputString); 

        // converts the inputString to an integer 
        inputInt = inputString.toInt();

        // resets the inputString 
        inputString="";
        Serial.println("the num of seconds to turn is: " + inputString); 

     // if the inputInt is greater than 0, turn the servo for that amount of seconds. 
     if (inputInt > 0){
      turnServo(inputInt, DispenserServo);   
      
          }
        }
      }
    }
    
   
// function to turn servo, takes in the time and servo to as input 
void  turnServo (int timeSec, Servo servo) {
    // get and store current time 
    timeNow = millis(); 

    // convert time to rotate the servo from seconds to milliseconds 
    timeMillis = (timeSec * 1000); 

    // print the time (debugging purposes) 
    Serial.println("the time in millis is " + String(timeMillis)); 

    // set servo positon to 180
    pos = 180; 
    servo.write(pos);
    delay(200);

    // while the time is less than the time inputted, vibrate servo 
    while(millis() < timeNow + timeMillis-220){
      vibrateServo(timeSec, servo, 40);   
}
//  return servo back to original position 
    returnServo(servo); 
  
}


// Function to vibrate the servo
// this function is called inside the vibrate servo function 
void vibrateServo (int timeSec, Servo servo, int degOfRotation) { 

  // move in one direction 
  servo.write(180-degOfRotation); 
  delay(250);

  // move in the other direction 
  servo.write(180+degOfRotation);
  delay(250); 

  // print to serial 
  Serial.println("Vibration Cycle Complete");
} 



// function to sreturn the servo back to it's starting position of 0 degrees 
void returnServo (Servo servo){
  servo.write(0); 
  pos = 0;
  delay(1000);  
}

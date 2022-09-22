 #include <SoftwareSerial.h>
#include <Stepper.h>


char input; 

const int STEPS = 64; // the number of steps in one revolution of your motor (28BYJ-48)

Stepper stepper(STEPS, 8, 10, 9, 11);
SoftwareSerial BT(2, 3); // RX | TX


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  BT.begin(9600);
  Serial.println("The bluetooth gates are open.\n Connect to HC-05 from any other bluetooth device with 1234 as pairing key!.");
}

void loop() {
  // put your main code here, to run repeatedly:
//   int numSteps = Serial.parseInt();
  if(BT.available()){
    Serial.write(BT.read());
  }
  if(Serial.available()){
    Serial.println("connected!");
    BT.write(Serial.read());
  }
    input = BT.read();  
    
    if (input == 'A'){

//    for( int i=0; i<2038; i++ )
//        {stepper.step(1);    //use whatever you need to step the motor
//          delay( 1000/2038 ); 
//          }
      
    Serial.println("A spin started");
    stepper.setSpeed(15);
    stepper.step(-64);

    }

    
    
//    }
//
//    else if (msg == 'B') {
//      stepper.setSpeed(400);
//      stepper.step(32);
//      Serial.println("B spin done");
//
//    }
//   else if (msg == 'C'){
//      stepper.setSpeed(0);
//      delay(5000);
//      Serial.println("No spin done");
//    }
//  
//}
  //    
//    if (isDigit(input)){
//      Serial.println(input);
//      String stringNum = String(input);
//      int steps = stringNum.toInt();
//      Serial.println(input);
//      stepper.setSpeed(600);
//      stepper.step(steps);
//    }
      
//
// 
//  // Feed all data from termial to bluetooth
//  if (Serial.available())
//    BT.write(Serial.read());

}

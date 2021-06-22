/* LED CONTROLLING WITH PYTHON

 * It's a ESP management through Python
 * It simply fetches the path from the request
 * Path is: https://example.com/this -> "/this"
 * You can command your esp through python with request paths
 * You can read the path with getPath() function
 */

/*
  * PIN CONNECTION :
  * D1 - RED
  * D2 - GREEN
  * D3 - BLUE
*/

/*
  * RED - Sleeping - LOW 
  * YELLOW - Staying alert and working - NORMAL
  * BLUE - Working out - EXCITED
  * PURPLE - Lowering anxiety - STRESS
*/
#include "ESP_MICRO.h"

void setup(){
  Serial.begin(9600);
  start("wifi name","wifi password"); // Wifi details to connect to

  pinMode(D1,OUTPUT);//RED
  pinMode(D2,OUTPUT);//GREEN
  pinMode(D3,OUTPUT);//BLUE
}

void loop(){
  waitUntilNewReq();  //Waits until a new request from python come

  /*
  if (getPath()=="/WHITE"){
    digitalWrite(D1, HIGH);
    digitalWrite(D2, HIGH);
    digitalWrite(D3, HIGH);
  }*/
  if(getPath()=="/NORMAL"){
    digitalWrite(D1, HIGH);
    digitalWrite(D2, HIGH);
    digitalWrite(D3, LOW);
  }
  if(getPath()=="/STRESS"){
    digitalWrite(D1, HIGH);
    digitalWrite(D2, LOW);
    digitalWrite(D3, HIGH);
  }

  if (getPath()=="/LOW"){
    digitalWrite(D1, HIGH);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
  }

  /*
  if (getPath()=="/TURQUOISE"){
    digitalWrite(D1, LOW);
    digitalWrite(D2, HIGH);
    digitalWrite(D3, HIGH);
  }

  if (getPath()=="/GREEN"){
    digitalWrite(D1, LOW);
    digitalWrite(D2, HIGH);
    digitalWrite(D3, LOW);
  }*/ 

  if (getPath()=="/EXCITED"){
    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, HIGH);
  }   

  if (getPath()=="/OFF"){
    digitalWrite(D1, LOW);
    digitalWrite(D2, LOW);
    digitalWrite(D3, LOW);
  }
}

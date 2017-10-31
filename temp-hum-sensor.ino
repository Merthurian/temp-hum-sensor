//Temperature and Humidity Logger. Dan Purcell 2017
//Based on code by Peter H Anderson, Baltimore, MD, Nov, '11
    
#include <Wire.h> //I2C library

void fetch_humidity_temperature(unsigned int *p_Humidity, unsigned int *p_Temperature);
void print_float(float f, int num_digits);

String inBuffer;

void setup(void)
{
   Serial.begin(9600);
   Wire.begin();
   delay(5000);
}

void loop(void)
{
  unsigned int H_dat, T_dat;
  float RH, T_C;
   
  while(1){
    
    inBuffer = "";
    
    while (Serial.available()){
      char c = Serial.read();
      inBuffer += c;
    }

    if (inBuffer == "next"){
      fetch_humidity_temperature(&H_dat, &T_dat);
    
      RH = (float) H_dat * 6.10e-3;
      T_C = (float) T_dat * 1.007e-2 - 40.0;

      print_float(RH, 1);
      Serial.print("  ");
      print_float(T_C, 2);
      Serial.println();

      delay(100);
    }
    else if (inBuffer == "hello")
      Serial.println("hello");
  }
}

void fetch_humidity_temperature(unsigned int *p_H_dat, unsigned int *p_T_dat)
{
      byte address, Hum_H, Hum_L, Temp_H, Temp_L, _status;
      unsigned int H_dat, T_dat;
      address = 0x27;;
      Wire.beginTransmission(address); 
      Wire.endTransmission();
      delay(100);
      
      Wire.requestFrom((int)address, (int) 4);
      Hum_H = Wire.read();
      Hum_L = Wire.read();
      Temp_H = Wire.read();
      Temp_L = Wire.read();
      Wire.endTransmission();
      
      Hum_H = Hum_H & 0x3f;
      H_dat = (((unsigned int)Hum_H) << 8) | Hum_L;
      T_dat = (((unsigned int)Temp_H) << 8) | Temp_L;
      T_dat = T_dat / 4;
      *p_H_dat = H_dat;
      *p_T_dat = T_dat;
}
   
void print_float(float f, int num_digits)
{
    int f_int;
    int pows_of_ten[4] = {1, 10, 100, 1000};
    int multiplier, whole, fract, d, n;

    multiplier = pows_of_ten[num_digits];
    if (f < 0.0)
    {
        f = -f;
        Serial.print("-");
    }
    whole = (int) f;
    fract = (int) (multiplier * (f - (float)whole));

    Serial.print(whole);
    Serial.print(".");

    for (n=num_digits-1; n>=0; n--) // print each digit with no leading zero suppression
    {
         d = fract / pows_of_ten[n];
         Serial.print(d);
         fract = fract % pows_of_ten[n];
    }
}      



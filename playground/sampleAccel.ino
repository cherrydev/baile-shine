#include <Adafruit_CircuitPlayground.h>
#include <Wire.h>
#include <SPI.h>
#include <limits.h>

unsigned long next = 0;
int sample_period = 5;

void setup() {
  // put your setup code here, to run once:
  while (!Serial);
  
  Serial.begin(19200);
  CircuitPlayground.begin();
  CircuitPlayground.setAccelRange(LIS3DH_RANGE_8_G);
  next = millis();
}

void loop() {
  if (millis() >= next) {
    Serial.println(CircuitPlayground.motionX());
    next = next + sample_period;
  }
  return;
}

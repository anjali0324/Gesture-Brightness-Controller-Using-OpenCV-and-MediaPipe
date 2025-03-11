int ledPin = 9;  // PWM Pin for LED
int brightness = 0;

void setup() {
    Serial.begin(9600);
    pinMode(ledPin, OUTPUT);
}

void loop() {
    if (Serial.available()) {
        brightness = Serial.parseInt();  // Read brightness from Python
        brightness = map(brightness, 0, 100, 0, 255);  // Scale to 0-255
        analogWrite(ledPin, brightness);  // Set LED brightness
    }
}

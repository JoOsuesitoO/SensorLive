// --- Definición de Pines ---
const int PinLuz = A0;  // Sensor de luz
const int PinTemp = A1; // Sensor de temperatura
const int pinAnt = A2;  // "Antena"
const int pinAgua = A3; // Sensor de agua

const byte llave = 100; 

void setup() {
  Serial.begin(9600);
}

void loop() {
  int ValorLuz = analogRead(PinLuz);
  int ValorTemp = analogRead(PinTemp);

  int Luz_Cifrada = ValorLuz ^ llave;
  int Temp_Cifrada = 53 ^ llave;

  int ValorAnt = analogRead(pinAnt);
  int ValorAgua = analogRead(pinAgua);

  int Ant_Cifrada = ValorAnt ^ llave;
  int Agua_Cifrada = ValorAgua ^ llave;

  Serial.println(Luz_Cifrada);
  Serial.println(Temp_Cifrada);
  Serial.println(Ant_Cifrada);
  Serial.println(Agua_Cifrada);
  Serial.println();
  delay(1000);

}

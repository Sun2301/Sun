/* 
 * Gesture Hero — Arduino Nano 33 BLE Sense
 * IMU → Edge Impulse → BLE
 * Arduino Days 2026 — Cotonou
 */

#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

//  bibliothèque exportée depuis Edge Impulse
#include <Mr_Sun-project-1_inferencing.h>


// ===== BLE Setup =====
BLEService gestureService("19B10000-E8F2-537E-4F6C-D104768A1214");
BLEStringCharacteristic gestureCharacteristic("19B10001-E8F2-537E-4F6C-D104768A1214", BLERead | BLENotify, 20);

// ===== Paramètres =====
#define CONFIDENCE_THRESHOLD  0.75   // Seuil de confiance minimum pour envoyer un geste
#define SAMPLE_COUNT          EI_CLASSIFIER_RAW_SAMPLE_COUNT
#define FEATURE_SIZE          EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE

float features[FEATURE_SIZE];

// ===== Collecte IMU =====
int raw_feature_get_data(size_t offset, size_t length, float *out_ptr) {
    memcpy(out_ptr, features + offset, length * sizeof(float));
    return 0;
}

void setup() {
    Serial.begin(115200);

    // Init IMU
    if (!IMU.begin()) {
        Serial.println("Erreur IMU !");
        while (1);
    }

    // Init BLE
    if (!BLE.begin()) {
        Serial.println("Erreur BLE !");
        while (1);
    }

    BLE.setLocalName("Sunnypulse");
    
    BLE.setAdvertisedService(gestureService);
    gestureService.addCharacteristic(gestureCharacteristic);
    BLE.addService(gestureService);
    BLE.advertise();

    Serial.println("Nano 33 prêt — en attente de connexion BLE...");
}

void loop() {
    BLEDevice central = BLE.central();

    if (central) {
        Serial.print("Connecté à : ");
        Serial.println(central.address());

        while (central.connected()) {
            // Collecter les données IMU
            int idx = 0;
            for (int i = 0; i < SAMPLE_COUNT; i++) {
    BLE.poll();  // ← ajouter cette ligne ici
    float ax, ay, az, gx, gy, gz;
    while (!IMU.accelerationAvailable() || !IMU.gyroscopeAvailable());
    IMU.readAcceleration(ax, ay, az);
    IMU.readGyroscope(gx, gy, gz);
    features[idx++] = ax;
    features[idx++] = ay;
    features[idx++] = az;
    features[idx++] = gx;
    features[idx++] = gy;
    features[idx++] = gz;
    delayMicroseconds(1000000 / 100);
}

            // Créer le signal pour Edge Impulse
            signal_t signal;
            signal.total_length = FEATURE_SIZE;
            signal.get_data = &raw_feature_get_data;

            // Inférence
            ei_impulse_result_t result;
            EI_IMPULSE_ERROR err = run_classifier(&signal, &result, false);

            if (err != EI_IMPULSE_OK) {
                Serial.print("Erreur inférence : ");
                Serial.println(err);
                continue;
            }

            // Trouver la classe avec la confiance max
            float maxConfidence = 0;
            String bestLabel = "idle";

            for (int i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
                if (result.classification[i].value > maxConfidence) {
                    maxConfidence = result.classification[i].value;
                    bestLabel = result.classification[i].label;
                }
            }

            // Envoyer seulement si confiance suffisante et pas idle
            if (maxConfidence >= CONFIDENCE_THRESHOLD && bestLabel != "idle") {
                Serial.print("Geste : ");
                Serial.print(bestLabel);
                Serial.print(" (");
                Serial.print(maxConfidence);
                Serial.println(")");

                gestureCharacteristic.writeValue(bestLabel);
            }
        }

        Serial.println("Déconnecté.");
    }
}

import Foundation
import IOBluetooth

// HID Descriptor for Android TV Remote
// This describes the device as a keyboard/consumer control device
let hidDescriptor: [UInt8] = [
    0x05, 0x01,        // Usage Page (Generic Desktop)
    0x09, 0x06,        // Usage (Keyboard)
    0xA1, 0x01,        // Collection (Application)
    0x05, 0x07,        //   Usage Page (Key Codes)
    0x19, 0x00,        //   Usage Minimum (0)
    0x29, 0xFF,        //   Usage Maximum (255)
    0x15, 0x00,        //   Logical Minimum (0)
    0x25, 0xFF,        //   Logical Maximum (255)
    0x75, 0x08,        //   Report Size (8)
    0x95, 0x08,        //   Report Count (8)
    0x81, 0x00,        //   Input (Data, Array)
    0xC0,              // End Collection
    
    // Consumer Control (for media keys)
    0x05, 0x0C,        // Usage Page (Consumer)
    0x09, 0x01,        // Usage (Consumer Control)
    0xA1, 0x01,        // Collection (Application)
    0x15, 0x00,        //   Logical Minimum (0)
    0x25, 0x01,        //   Logical Maximum (1)
    0x75, 0x01,        //   Report Size (1)
    0x95, 0x08,        //   Report Count (8)
    0x09, 0xB5,        //   Usage (Scan Next Track)
    0x09, 0xB6,        //   Usage (Scan Previous Track)
    0x09, 0xE9,        //   Usage (Volume Up)
    0x09, 0xEA,        //   Usage (Volume Down)
    0x09, 0xE2,        //   Usage (Mute)
    0x09, 0xCD,        //   Usage (Play/Pause)
    0x81, 0x02,        //   Input (Data, Variable, Absolute)
    0xC0               // End Collection
]

class BluetoothHIDServer: NSObject {
    var sdpRecord: IOBluetoothSDPServiceRecord?
    var hidDevice: IOBluetoothL2CAPChannel?
    
    func start() {
        print("Starting Bluetooth HID Server...")
        print("Device Name: VSeeBox Remote")
        
        // Create SDP record for HID device
        let serviceDict: [String: Any] = [
            "ServiceName": "VSeeBox Remote",
            "ServiceDescription": "Android TV Remote Control",
            "ProviderName": "Sports Monitor",
            IOBluetoothSDPAttributeIdentifierServiceClassIDList: [
                IOBluetoothSDPUUID(uuid16: 0x1124) // HID Service Class
            ],
            IOBluetoothSDPAttributeIdentifierProtocolDescriptorList: [
                [
                    IOBluetoothSDPUUID(uuid16: 0x0100), // L2CAP
                    11 // HID Control PSM
                ],
                [
                    IOBluetoothSDPUUID(uuid16: 0x0011) // HIDP
                ]
            ],
            "HIDDescriptor": Data(hidDescriptor)
        ]
        
        // Publish SDP service
        var record: IOBluetoothSDPServiceRecord?
        let result = IOBluetoothSDPServiceRecord.publishedServiceRecord(
            withDictionary: serviceDict as NSDictionary,
            serviceRecord: &record
        )
        
        if result == kIOReturnSuccess, let record = record {
            self.sdpRecord = record
            print("✓ HID Service published")
            print("✓ Device is now discoverable as 'VSeeBox Remote'")
            print("\nPair from VSeeBox: Settings → Bluetooth → VSeeBox Remote")
            print("\nPress Ctrl+C to stop")
            
            // Keep running
            RunLoop.main.run()
        } else {
            print("✗ Failed to publish HID service: \(result)")
        }
    }
    
    func sendKeyPress(_ keyCode: UInt8) {
        // Send HID report
        var report: [UInt8] = [0x01, keyCode, 0, 0, 0, 0, 0, 0, 0]
        // TODO: Send via L2CAP channel when connected
        print("Sending key: 0x\(String(keyCode, radix: 16))")
    }
}

// Main
print("=== Bluetooth HID Virtual Remote ===\n")

let server = BluetoothHIDServer()
server.start()

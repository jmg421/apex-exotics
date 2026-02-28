#!/usr/bin/env python3
"""
Document Scanner Integration - Minimal Implementation
Epson ES-580W integration for legal document digitization
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentScanner:
    """
    Minimal document scanner for Epson ES-580W
    Focuses on legal document digitization with proper naming
    """
    
    def __init__(self, output_dir: str = "./scanned_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def check_scanner_available(self) -> bool:
        """Check if Epson scanner is available via SANE"""
        try:
            result = subprocess.run(['scanimage', '-L'], 
                                  capture_output=True, text=True, timeout=10)
            return 'epson' in result.stdout.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("SANE scanimage not found - install with: brew install sane-backends")
            return False
    
    def scan_document(self, 
                     document_type: str = "evidence", 
                     case_id: str = "palisade",
                     description: str = "") -> Optional[str]:
        """
        Scan document with legal naming convention
        Returns path to scanned file or None if failed
        """
        if not self.check_scanner_available():
            print("❌ Scanner not available. Install SANE: brew install sane-backends")
            return None
        
        # Generate filename with timestamp and case info
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_desc = safe_desc.replace(' ', '_')
        
        filename = f"{case_id}_{document_type}_{timestamp}"
        if safe_desc:
            filename += f"_{safe_desc}"
        filename += ".pdf"
        
        output_path = self.output_dir / filename
        
        print(f"📄 Scanning document: {filename}")
        print("   Place document in scanner and press Enter to continue...")
        input()
        
        try:
            # Scan command for Epson ES-580W
            # High quality: 300 DPI, PDF output
            cmd = [
                'scanimage',
                '--device-name=epson2:libusb:001:004',  # May need adjustment
                '--format=pdf',
                '--resolution=300',
                '--mode=Color',
                f'--output={output_path}'
            ]
            
            print("🔄 Scanning in progress...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and output_path.exists():
                print(f"✅ Document scanned successfully: {output_path}")
                
                # Log the scan for audit trail
                self._log_scan(filename, document_type, description)
                
                return str(output_path)
            else:
                print(f"❌ Scan failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Scan timeout - check scanner connection")
            return None
        except Exception as e:
            print(f"❌ Scan error: {e}")
            return None
    
    def _log_scan(self, filename: str, doc_type: str, description: str):
        """Log scan for audit trail"""
        log_file = self.output_dir / "scan_log.txt"
        timestamp = datetime.now().isoformat()
        
        with open(log_file, 'a') as f:
            f.write(f"{timestamp},{filename},{doc_type},{description}\n")
    
    def list_scanned_documents(self) -> list:
        """List all scanned documents"""
        if not self.output_dir.exists():
            return []
        
        docs = []
        for pdf_file in self.output_dir.glob("*.pdf"):
            stat = pdf_file.stat()
            docs.append({
                'filename': pdf_file.name,
                'size_mb': round(stat.st_size / 1024 / 1024, 2),
                'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M")
            })
        
        return sorted(docs, key=lambda x: x['created'], reverse=True)

# Integration with VIN decoder for case management
def scan_vin_related_document(vin: str, document_type: str, description: str = ""):
    """Scan document related to specific VIN"""
    scanner = DocumentScanner()
    
    # Use VIN as case identifier
    case_id = f"VIN_{vin[-6:]}"  # Last 6 digits for brevity
    
    return scanner.scan_document(
        document_type=document_type,
        case_id=case_id,
        description=description
    )

if __name__ == "__main__":
    scanner = DocumentScanner()
    
    print("=== Epson ES-580W Document Scanner ===")
    print(f"Output directory: {scanner.output_dir}")
    
    if scanner.check_scanner_available():
        print("✅ Scanner detected")
        
        # Example: Scan a service invoice for the Palisade case
        result = scan_vin_related_document(
            vin="KM8R54HE1LU066808",
            document_type="service_invoice",
            description="Great Lakes Hyundai 2025-09-20"
        )
        
        if result:
            print(f"Document ready for shredding: Original can be destroyed")
    else:
        print("❌ Scanner not found")
        print("Install SANE backends: brew install sane-backends")
    
    print("\n=== Scanned Documents ===")
    for doc in scanner.list_scanned_documents():
        print(f"📄 {doc['filename']} ({doc['size_mb']} MB) - {doc['created']}")

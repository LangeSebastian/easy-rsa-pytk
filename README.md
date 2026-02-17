# Easy-RSA PyTk Manager

A Python 3 Tkinter-based GUI for Easy-RSA certificate authority management, designed for Raspberry Pi with a 3.5" touchscreen (480x320px). Features a jog-dial navigation interface for keyboard-free operation.

## Features

- **Jog-Dial Navigation**: Navigate entirely with Up/Down/Confirm buttons (no keyboard required)
- **CA Management**: Initialize PKI, build CA, manage certificate authority
- **Certificate Operations**:
  - Create server and client certificates from templates
  - Sign certificate requests imported from USB
  - List and manage certificates
  - Revoke certificates with CRL generation
  - Export certificates to USB
- **Template System**: Pre-configured templates for common certificate types (CA, server, client, VPN)
- **USB Support**: Import/export certificates, CSRs, and templates via USB drives
- **Optimized UI**: Custom widgets designed for small 480x320 display

## Hardware Requirements

- Raspberry Pi (any model with GPIO)
- 3.5" touchscreen display (480x320 resolution)
- USB port for file exchange
- Optional: Physical Up/Down/Confirm buttons (can use keyboard for testing)

## Software Requirements

- Raspberry Pi OS (or any Linux distribution)
- Python 3.7 or higher
- Easy-RSA 3.x installed
- Tkinter (usually included with Python)

## Installation

### 1. Install Easy-RSA

```bash
sudo apt-get update
sudo apt-get install easy-rsa
```

### 2. Clone Repository

```bash
git clone https://github.com/LangeSebastian/easy-rsa-pytk.git
cd easy-rsa-pytk
```

### 3. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Configure Settings (Optional)

Edit `config/defaults.json` to customize:
- PKI directory path
- Easy-RSA binary location
- USB mount points
- Display settings

## Usage

### Running the Application

```bash
python3 main.py
```

For fullscreen mode (recommended on Raspberry Pi):
```bash
python3 main.py  # Fullscreen is default
```

### Navigation

- **Up Button** (or ↑ key): Move selection up
- **Down Button** (or ↓ key): Move selection down
- **Confirm Button** (or Enter key): Confirm selection
- **Escape key**: Exit fullscreen (testing only)

### Typical Workflow

#### 1. Initialize PKI and Create CA

1. Navigate to **Settings** > **CA Management**
2. Select **Initialize PKI**
3. Confirm initialization
4. Select **Build CA**
5. Choose a CA template (e.g., `ca`)
6. Confirm CA creation

#### 2. Create Server Certificate

1. Navigate to **Certificates** > **Create Certificate**
2. Select **Server Certificate** or **VPN Server Certificate**
3. Enter certificate name character-by-character using Up/Down/Confirm
4. Select **[DONE]** when finished
5. Confirm creation

#### 3. Create Client Certificate

1. Navigate to **Certificates** > **Create Certificate**
2. Select **Client Certificate** or **VPN Client Certificate**
3. Enter certificate name
4. Confirm creation

#### 4. Sign Certificate Request

1. Import CSR from USB: **USB Import/Export** > Select USB drive > **Import Certificate Requests**
2. Navigate to **Certificates** > **Sign Certificate Request**
3. Select the imported request
4. Choose certificate type (server/client)
5. Confirm signing

#### 5. Export Certificates to USB

1. Navigate to **USB Import/Export**
2. Select your USB drive
3. Choose **Export Certificates**
4. Select certificate to export
5. Choose full bundle (cert + key + CA) or certificate only

## Directory Structure

```
easy-rsa-pytk/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── config/
│   ├── defaults.json      # Default configuration
│   └── settings.py        # Settings manager
├── ui/
│   ├── app.py             # Main application window
│   ├── layout.py          # Split layout manager
│   ├── jogdial.py         # Jog-dial navigation
│   ├── widgets.py         # Custom widgets
│   └── screens/           # UI screens
├── easyrsa/
│   ├── wrapper.py         # Easy-RSA command wrapper
│   ├── parser.py          # Output parsing
│   ├── pki.py             # PKI management
│   └── models.py          # Data models
├── usb/
│   ├── detector.py        # USB drive detection
│   └── manager.py         # File import/export
├── templates/
│   ├── manager.py         # Template management
│   └── vars/              # Template files
└── utils/
    ├── logger.py          # Logging utilities
    └── validation.py      # Input validation
```

## Configuration

### PKI Directory

Default: `/home/pi/easy-rsa-pki`

Change in `config/defaults.json`:
```json
{
  "pki_dir": "/path/to/your/pki"
}
```

### Easy-RSA Binary

Default: `/usr/share/easy-rsa/easyrsa`

Change in `config/defaults.json`:
```json
{
  "easyrsa_bin": "/path/to/easyrsa"
}
```

### USB Mount Points

Default: `["/media/pi", "/mnt/usb"]`

Add custom mount points in `config/defaults.json`:
```json
{
  "usb_mount_points": [
    "/media/pi",
    "/mnt/usb",
    "/custom/mount"
  ]
}
```

## Templates

The application includes pre-configured templates:

- **ca.vars**: Certificate Authority
- **server.vars**: Generic server certificate
- **client.vars**: Generic client certificate
- **vpn-server.vars**: OpenVPN server certificate
- **vpn-client.vars**: OpenVPN client certificate

### Creating Custom Templates

1. Create a `.vars` file in `templates/vars/`
2. Use `set_var` format:

```bash
set_var EASYRSA_REQ_COUNTRY "US"
set_var EASYRSA_REQ_PROVINCE "California"
set_var EASYRSA_REQ_CITY "San Francisco"
set_var EASYRSA_REQ_ORG "My Organization"
set_var EASYRSA_REQ_EMAIL "admin@example.com"
set_var EASYRSA_REQ_OU "IT Department"
set_var EASYRSA_KEY_SIZE 2048
set_var EASYRSA_CERT_EXPIRE 825
```

## Troubleshooting

### Application Won't Start

- Check Python version: `python3 --version` (requires 3.7+)
- Verify Tkinter is installed: `python3 -c "import tkinter"`
- Check Easy-RSA is installed: `which easyrsa`

### No USB Drives Detected

- Verify USB is mounted: `mount | grep usb`
- Check mount points in settings match your system
- Ensure USB is formatted with a compatible filesystem (ext4, FAT32, NTFS)

### Certificate Creation Fails

- Verify PKI is initialized: Check **Settings** > **PKI Settings**
- Ensure CA exists: Check **Settings** > **CA Management** > **CA Status**
- Check Easy-RSA binary path in settings

### Display Issues

- Adjust font sizes in `config/defaults.json`
- Modify layout dimensions for different screen sizes
- Check display resolution settings on Raspberry Pi

## Development

### Running Tests

```bash
python3 -m pytest tests/
```

### Code Structure

- **UI Layer**: `ui/` - Tkinter interface, navigation, widgets
- **Business Logic**: `easyrsa/` - Certificate operations, PKI management
- **Integration**: `usb/` - USB operations, `templates/` - Template management
- **Configuration**: `config/` - Settings and defaults

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [Easy-RSA](https://github.com/OpenVPN/easy-rsa)
- Designed for Raspberry Pi and small touchscreens
- Inspired by the need for simple, keyboard-free PKI management

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Review [common issues](docs/troubleshooting.md)

## Roadmap

- [ ] Certificate expiration warnings
- [ ] Batch certificate generation
- [ ] Advanced CRL management
- [ ] Certificate backup/restore
- [ ] Network sync support (optional online mode)
- [ ] Hardware button GPIO integration
- [ ] Multi-language support

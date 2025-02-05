# Secure Headless Raspberry Pi Setup with SSH Keys, Firewall, Fail2Ban, PSAD, and Google Authenticator

## Table of Contents

1. Introduction
2. Installing Raspberry Pi OS Headless
3. Enabling SSH and Setting Up SSH Keys
4. Configuring the Firewall with UFW
5. Setting Up Google Authenticator for SSH 2FA
6. Setting Up Fail2Ban to Prevent Brute-Force Attacks
7. Setting Up PSAD to Detect Port Scans
8. Configuring Unattended Security Updates
9. Configuring Email Notifications for Security Alerts
10. Testing Nmap for Vulnerability Assessment
11. Restricting SSH Access to a Single Machine
12. Final Security Checks and Testing

---

## 1. Introduction

This guide walks through setting up a Raspberry Pi without a screen, configuring SSH keys for secure access, enforcing strict firewall rules, using **Fail2Ban** and **PSAD** for intrusion detection, enabling **email alerts**, setting up **Google Authenticator for two-factor authentication**, and **restricting access to only one machine**. Additionally, this guide covers how to install the system in a headless setup (without a monitor or keyboard).

---

## 2. Installing Raspberry Pi OS Headless

### 2.1 Download and Flash Raspberry Pi OS

1. Download Raspberry Pi OS (Lite) from [Raspberry Pi Website](https://www.raspberrypi.org/software/operating-systems/)
2. Flash the OS to an SD card using **Raspberry Pi Imager** or **balenaEtcher**

### 2.2 Enable SSH and Wi-Fi Before First Boot

After flashing, mount the `boot` partition and create:

- An empty file named `ssh` to enable SSH:
  ```sh
  touch /Volumes/boot/ssh
  ```
- A file `wpa_supplicant.conf` for Wi-Fi:
  ```sh
  cat <<EOF > /Volumes/boot/wpa_supplicant.conf
  country=US
  ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
  update_config=1
  network={
      ssid="YOUR_WIFI_SSID"
      psk="YOUR_WIFI_PASSWORD"
  }
  EOF
  ```

### 2.3 Enable SSH with Ethernet Instead of Wi-Fi
During the installation process, use advanced settings to enable SSH access. Ensure you set up the correct username and password. Insert the SD card and start the Raspberry Pi.

---


## 3. Enabling SSH and Setting Up SSH Keys

To find the Raspberry Pi's IP address, log in to your router or use nmap:
```sh
nmap -sn 192.168.1.0/24 | grep "Raspberry"
```

### 3.1 Generating SSH Keys on Windows

To create a secure SSH key pair on Windows:
1. Open **PowerShell** and run:
   ```sh
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```
2. Save the key pair in the default location (`C:\Users\YourUser\.ssh\id_rsa`).
3. Upload the **public key** (`id_rsa.pub`) to the Raspberry Pi:
   ```sh
   scp C:\Users\YourUser\.ssh\id_rsa.pub pi@<RaspberryPi-IP>:~/.ssh/authorized_keys
   ```

**Pro Tip:** Store your private SSH key in a secure **password manager** like Bitwarden or 1Password. Although it might be inconvenient, it significantly enhances security and aligns with the **CIA Triad** principles.

### 3.2 Connect via SSH
```sh
ssh pi@<RaspberryPi-IP>
```
Default password: `raspberry`

### 3.3 Disable Password Authentication and Enforce SSH Key Usage
```sh
sudo nano /etc/ssh/sshd_config
```
Modify:
```ini
PasswordAuthentication no
ChallengeResponseAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```
Restart SSH:
```sh
sudo systemctl restart ssh
```

---


## 4. Configuring the Firewall with UFW

```sh
sudo apt update && sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default deny outgoing
sudo ufw allow from 192.168.1.100 to any port 22 proto tcp
sudo ufw allow out to 192.168.1.1 port 53 proto udp
sudo ufw allow out to 8.8.8.8 port 53 proto udp
sudo ufw enable
```

---

## 5. Setting Up Google Authenticator for SSH 2FA

### Why Use Google Authenticator?

Google Authenticator enhances SSH security by requiring a time-based one-time password (TOTP) in addition to your SSH key. This ensures that even if an attacker gains access to your SSH key, they will still need the dynamic code generated on your authentication app to log in.

To use Google Authenticator, you need a TOTP-compatible app such as:

- **Google Authenticator (Android/iOS)**
- **Authy (Android/iOS/Windows/Mac) - Supports cloud backups**
- **FreeOTP (Android/iOS) - Open-source alternative**

These apps generate temporary codes that refresh every 30 seconds, providing an extra layer of protection.

### Installation and Configuration

1. Install the necessary package:
   ```sh
   sudo apt install libpam-google-authenticator -y
   ```

2. Run the setup tool:
   ```sh
   google-authenticator
   ```
   Answer **Yes** to the prompts:
   - Use time-based authentication (**Yes**)
   - Update `.google_authenticator` (**Yes**)
   - Disallow multiple uses (**Yes**)
   - Extend rate-limiting (**Yes**)

3. **Scan the QR code** displayed on your screen using an authentication app:
   - Open **Google Authenticator** or **Authy**
   - Select **Add Account** → **Scan QR Code**
   - Scan the code displayed in the terminal
   - Backup the emergency codes provided

4. Enable Google Authenticator for SSH authentication:
   ```sh
   sudo nano /etc/pam.d/sshd
   ```
   Add the following line at the top:
   ```ini
   auth required pam_google_authenticator.so
   ```

5. Restart SSH to apply changes:
   ```sh
   sudo systemctl restart ssh
   ```

Now, when logging in via SSH, you will be prompted for both your SSH key and a time-based one-time password (TOTP) from your authenticator app.

Ensure you have your authentication app ready before logging out, as failing to have access to your TOTP can lock you out of your Raspberry Pi.

---

## 6. Configuring Unattended Security Updates

To ensure the Raspberry Pi stays up to date with critical security patches, configure automatic security updates.

1. Install the **unattended-upgrades** package:
   ```sh
   sudo apt install unattended-upgrades -y
   ```
2. Enable automatic updates:
   ```sh
   sudo dpkg-reconfigure --priority=low unattended-upgrades
   ```
3. Configure the update settings:
   ```sh
   sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
   ```
   Ensure the following lines are present:
   ```ini
   Unattended-Upgrade::Allowed-Origins {
       "${distro_id}:${distro_codename}-security";
   };
   Unattended-Upgrade::Automatic-Reboot "true";
   ```
4. Apply changes:
   ```sh
   sudo systemctl enable unattended-upgrades
   sudo systemctl restart unattended-upgrades
   ```

Now, your system will automatically install security updates, reducing the risk of vulnerabilities.

---

## 7. Configuring Email Notifications for Security Alerts

Setting up email notifications ensures you receive alerts for security-related events.

1. Install **mailutils**:
   ```sh
   sudo apt install mailutils -y
   ```
2. Configure email settings in **ssmtp**:
   ```sh
   sudo nano /etc/ssmtp/ssmtp.conf
   ```
   Example settings:
   ```ini
   root=your_email@example.com
   mailhub=smtp.gmail.com:587
   AuthUser=your_email@example.com
   AuthPass=your_email_password
   UseTLS=YES
   ```
3. Test email sending:
   ```sh
   echo "Security Test Email" | mail -s "Raspberry Pi Alert" your_email@example.com
   ```

---

## 8. Setting Up PSAD to Detect Port Scans

PSAD (Port Scan Attack Detector) is an intrusion detection system that monitors firewall logs to detect potential scanning activity.

### 8.1 Install PSAD

1. Install the required package:
   ```sh
   sudo apt update && sudo apt install psad -y
   ```

2. Enable UFW logging:
   ```sh
   sudo ufw logging on
   ```

3. Configure UFW to log packets:
   ```sh
   sudo nano /etc/ufw/before.rules
   ```
   Add the following lines at the beginning of the file:
   ```ini
   -A INPUT -j LOG
   -A FORWARD -j LOG
   ```
   Save and exit the file, then restart UFW:
   ```sh
   sudo systemctl restart ufw
   ```

### 8.2 Configure PSAD

1. Edit the PSAD configuration file:
   ```sh
   sudo nano /etc/psad/psad.conf
   ```
   Modify the following lines:
   ```ini
   EMAIL_ADDRESSES your_email@example.com;
   HOSTNAME your_pi_hostname;
   ENABLE_AUTO_IDS Y;
   AUTO_IDS_DANGER_LEVEL 3;
   EMAIL_ALERT_DANGER_LEVEL 1;
   HOST_SCAN_THRESHOLD 5;
   PSADWATCHDOG 3600;
   ```
   ✅ `AUTO_IDS_DANGER_LEVEL 3;` → Aggressive auto-blocking.
   ✅ `EMAIL_ALERT_DANGER_LEVEL 1;` → Ensures alerts for all scans.
   ✅ `HOST_SCAN_THRESHOLD 5;` → Reduces the threshold for detecting scans.
   ✅ `PSADWATCHDOG 3600;` → Ensures PSAD runs continuously.
   
   Save the file and restart PSAD:
   ```sh
   sudo systemctl restart psad
   ```

### 8.3 Update PSAD Signatures

Ensure PSAD has the latest attack signatures:
```sh
sudo psad --sig-update
sudo psad -R
sudo systemctl restart psad
```

### 8.4 Ensure iptables is Hooked

Check if the PSAD chain has active rules:
```sh
sudo iptables -L PSAD -n
```
If empty, manually add a blocking rule:
```sh
sudo iptables -I INPUT -m psad --psad-detect -j DROP
```
Then restart PSAD again:
```sh
sudo systemctl restart psad
```

### 8.5 Verify PSAD Status

Check if PSAD is running and monitoring logs properly:
```sh
sudo psad --Status
```

PSAD will now monitor for port scanning activity, enforce automatic blocking, and send alerts if any suspicious behavior is detected.

---

Your Raspberry Pi is now hardened with security best practices, automated updates, intrusion detection, and multi-factor authentication. 🚀





## 9. Testing Nmap for Vulnerability Assessment

Regular network scanning helps identify vulnerabilities.
```sh
nmap -A -T4 <RaspberryPi-IP>
```

---

## 10. Restricting SSH Access to a Single Machine

To limit SSH access to one trusted device:
```sh
sudo nano /etc/hosts.allow
```
Add:
```ini
sshd: 192.168.1.100
```
```sh
sudo nano /etc/hosts.deny
```
Add:
```ini
sshd: ALL
```

---

## 11. Final Security Checks and Testing

1. Check firewall status:
   ```sh
   sudo ufw status verbose
   ```
2. Verify **Fail2Ban** and **PSAD**:
   ```sh
   sudo fail2ban-client status sshd
   sudo psad --Status
   ```
3. Test SSH login from an unauthorized device to ensure restrictions work.

---








# Secure Headless Raspberry Pi Setup with SSH Keys, Firewall, Fail2Ban, PSAD, and Google Authenticator

## Table of Contents

1. Introduction
2. Installing Raspberry Pi OS Headless
3. Enabling SSH and Setting Up SSH Keys
4. Configuring the Firewall with UFW
5. Setting Up Google Authenticator for SSH 2FA
6. Setting Up Fail2Ban to Prevent Brute-Force Attacks
7. Setting Up PSAD to Detect Port Scans
8. Configuring Email Notifications for Security Alerts
9. Testing Nmap for Vulnerability Assessment
10. Restricting SSH Access to a Single Machine
11. Final Security Checks and Testing

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

### 3.1 Connect via SSH
```sh
ssh pi@<RaspberryPi-IP>
```
Default password: `raspberry`

### 3.2 Disable Password Authentication and Enable Key-Based Login
```sh
mkdir -p ~/.ssh && chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
```
Paste your **public SSH key** and save.

```sh
sudo nano /etc/ssh/sshd_config
```
Modify:
```ini
PasswordAuthentication yes
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

## 6-11. Remaining Steps

The remaining sections cover setting up **Fail2Ban, PSAD, email notifications, security testing**, and **finalizing your Raspberry Pi's security setup**.


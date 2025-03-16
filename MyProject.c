 // LED interface
sbit LCD_RS at RD0_bit;
sbit LCD_EN at RD1_bit;
sbit LCD_D4 at RD2_bit;
sbit LCD_D5 at RD3_bit;
sbit LCD_D6 at RD4_bit;
sbit LCD_D7 at RD5_bit;

// LCD PIN direction
sbit LCD_RS_DIRECTION at TRISD.B0;
sbit LCD_EN_DIRECTION at TRISD.B1;
sbit LCD_D4_DIRECTION at TRISD.B2;
sbit LCD_D5_DIRECTION at TRISD.B3;
sbit LCD_D6_DIRECTION at TRISD.B4;
sbit LCD_D7_DIRECTION at TRISD.B5;

// User pin declaration
sbit LED1 at PORTB.B1;
sbit LED3 at PORTB.B3;
sbit LED4 at PORTB.B4;
sbit LED5 at PORTB.B6; // LED5 on RB6
sbit SW at PORTB.B2;
sbit motor at PORTD.B6;

// Button inputs
sbit BTN1 at PORTC.B0; // Button for LED3
sbit BTN2 at PORTC.B1; // Button for LED4
sbit BTN3 at PORTC.B2; // Button for LED1
sbit BTN4 at PORTC.B3; // Button for LED5
sbit BTN_PASS1 at PORTC.B4; // Button for password digit '1'
sbit BTN_PASS2 at PORTC.B5; // Button for password digit '2'
sbit BTN_PASS3 at PORTC.B6; // Button for password digit '3'

// Button directions
sbit BTN1_DIR at TRISC.B0;
sbit BTN2_DIR at TRISC.B1;
sbit BTN3_DIR at TRISC.B2;
sbit BTN4_DIR at TRISC.B3;
sbit BTN_PASS1_DIR at TRISC.B4;
sbit BTN_PASS2_DIR at TRISC.B5;
sbit BTN_PASS3_DIR at TRISC.B6;

// Function to update LCD with LED state
void update_lcd(char led, char state) {
    char message[16];

    // Build the message manually
    message[0] = 'L';
    message[1] = 'E';
    message[2] = 'D';
    message[3] = led + '0'; // Convert number to character
    message[4] = ' ';
    message[5] = 'i';
    message[6] = 's';
    message[7] = ' ';
    message[8] = state == 1 ? 'O' : 'O';
    message[9] = state == 1 ? 'N' : 'F';
    message[10] = state == 1 ? ' ' : 'F';
    message[11] = '\0'; // Null-terminate the string

    // Display the message on the LCD
    switch (led) {
        case 1:
            Lcd_Out(1, 1, message);
            break;
        case 3:
            Lcd_Out(2, 1, message);
            break;
        case 4:
            Lcd_Out(3, 1, message);
            break;
        case 5:
            Lcd_Out(4, 1, message);
            break;
    }
}

// Function to get password
char get_password() {
    char password[4] = {0, 0, 0, 0};
    int i;

    while (1) {
        Lcd_Cmd(_LCD_CLEAR);
        Lcd_Out(1, 2, "Enter password:");

        for (i = 0; i < 3; i++) {
            while (1) {
                if (BTN_PASS1) { password[i] = '1'; while (BTN_PASS1); break; }
                if (BTN_PASS2) { password[i] = '2'; while (BTN_PASS2); break; }
                if (BTN_PASS3) { password[i] = '3'; while (BTN_PASS3); break; }
            }
            Lcd_Chr(2, i + 1, '*');
            Delay_ms(100);
        }

        if (strcmp(password, "123") == 0) {
            return 1; // Correct password
        } else {
            Lcd_Cmd(_LCD_CLEAR);
            Lcd_Out(1, 1, "Wrong Password!");
            Delay_ms(1000);
            memset(password, 0, sizeof(password)); // Reset password array
        }
    }
}

void main() {
    char x;
    // Initialize LCD
    Lcd_Init();
    Lcd_Cmd(_LCD_CURSOR_OFF);
    Lcd_Cmd(_LCD_CLEAR);

    // Call password function
    get_password();

    // Welcome message
    Lcd_Cmd(_LCD_CLEAR);
    Lcd_Out(1, 3, "Welcome!");
    motor = 1;
    Delay_ms(1500);
    motor = 0;

    // Main loop
    while (1) {
        // Check the state of SW
        if (SW == 1) {
            LED1 = 0;
            LED3 = 0;
            LED4 = 0;
            LED5 = 0; // Turn off LED5
            continue; // Skip the rest of the loop
        }

        // Check push buttons
        if (BTN1) { // Button 1 pressed
            LED3 = !LED3;
            update_lcd(3, LED3);
            while (BTN1); // Wait for release
        } else if (BTN2) { // Button 2 pressed
            LED4 = !LED4;
            update_lcd(4, LED4);
            while (BTN2); // Wait for release
        } else if (BTN3) { // Button 3 pressed
            LED1 = !LED1;
            update_lcd(1, LED1);
            while (BTN3); // Wait for release
        } else if (BTN4) { // Button 4 pressed
            LED5 = !LED5;
            update_lcd(5, LED5);
            while (BTN4); // Wait for release
        }?
    }
}
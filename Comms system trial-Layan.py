import random #used many times throughout the code
import time #used in both latency and in the log to show the date and time.
import GNSS_Symulation #the simulation file (I unfortunately misspelled simulation)
import string

#the globals
transmission_log = []
message_counter = 1 #this is the ID for each message (starts at 0 everytime the code is rerun)
emergency_mode = False
encryption_mode = False

def clean_output(text):
    return ''.join(c for c in text if c in string.printable)

#dictionary of the list of astronauts
astros = {
    1: {"name": "Astronaut-1", "position": GNSS_Symulation.astronauts[0]},
    2: {"name": "Astronaut-2", "position": GNSS_Symulation.astronauts[1]},
    3: {"name": "Astronaut-3", "position": GNSS_Symulation.astronauts[2]},
    4: {"name": "Astronaut-4", "position": GNSS_Symulation.astronauts[3]}
}

#this is kind of like a list of all the astronauts and rovers for the different senders and emergencies
system_status = {}
for i in range(1, 5):
    system_status[f"Astronaut-{i}"] = {"status": "normal", "emergency_type": None}
for i in range(1, 17):
    system_status[f"Rover-{i}"] = {"status": "normal", "emergency_type": None}


#this is the function that will basically print things into the log, with all the different statuses, and it prints in red if there is an emergency. 
def show_log():
    print("\n---Transmission Log---")
    for entry in transmission_log:
        if entry["Emergency Override"]:
            color = "\033[91m"
        else:
            color = "\033[0m"

        final_msg = entry.get("Message", "N/A")

        print(f"{color}[{entry['Time Stamp']}] Message {entry['Message ID']} by {entry['Sender Name']} at {entry['Sender Position']}: "
              f"{entry['Status']} after {entry['Attempts']} attempt(s) | "
              f"Encrypted: {entry['Encrypted']} | Emergency: {entry['Emergency Override']} | "
              f"Latency: {entry['Latency']}s | Message: '{final_msg}'\033[0m")




#this is the function that actually adds all the different entries into the log, and appends it to the appropriate file. 
def log_transmission(message_id, attempts, encryption_used, emergency_override, success, encrypted_message, sender_name, sender_position, latency, final_message):
    
    if success:
        status = "Success"
    else:
        status = "Failed"
    
    log_entry = {
        "Message ID" : message_id,
        "Sender Name" : sender_name,
        "Sender Position" : sender_position,
        "Message": final_message,
        "Attempts" : attempts, 
        "Encrypted" : encryption_used,
        "Emergency Override" : emergency_override, 
        "Status" : status,
        "Binary Message" : encrypted_message,
        "Latency" : latency,
        "Time Stamp" : time.strftime("%Y-%m-%d %H:%M:%S")
    }
    transmission_log.append(log_entry)


#this function ensures that the log is saved and not overwritten every time the code is run. 
def save_log(filename = "transmission_log.txt"):
    with open(filename, "a") as file:
        file.write("---Lunar Transmission Log---\n")
        file.write("---New Save---\n")
        for entry in transmission_log:
            file.write(f"[{entry['Time Stamp']}] Message {entry['Message ID']} by {entry['Sender Name']} at {entry['Sender Position']}: "
           f"{entry['Status']} after {entry['Attempts']} attempt(s) | "
           f"Encrypted: {entry['Encrypted']} | Emergency: {entry['Emergency Override']} | "
           f"Latency: {entry['Latency']}s\n")
    
    print(f"Log saved to {filename}")


#this prints when the transmission is successful, if its in emergency it shows the position of the sender, if not it jst shows the number of tries.
#I have commented the number of tries part out, as it was used earlier to debug but is not required anymore. I have kept it as part of the code incase it is required.
def print_transmission_success(recovered_text, emergency_override, tries, sender_name, sender_position):  
    if emergency_override:
        rounded_pos = (round(sender_position[0], 2), round(sender_position[1], 2))
        #print(f"\033[91mEmergency transmission successful after {tries} attempts\033[0m")
        print(f"\033[91m{sender_name} at {rounded_pos}: {recovered_text}\033[0m")
    
    else:
        #print(f"\033[92mFinal transmission successful after {tries} attempts\033[0m")
        print(f"\033[92m{sender_name}: {recovered_text}\033[0m")


#turns the text into binary using the ASCII system 
#it makes every character into its ASCII equivalent, and then changes the ASCII number into binary.
def text_into_binary(text):
    result = ''
    for char in text:
        ASCII = ord(char)
        binary = format(ASCII, '08b')
        result += binary
    return result


#does the opposite of the text_into_binary function. turns the binary back into text
#it splits up the binary message into 8 bit chunks and then switches them back into text.
def binary_into_text(binary):
    r= range(0, len(binary), 8)
    result = ''
    for i in r:
        smaller = binary[i:i+8]
        decimal = int(smaller, 2)
        char = chr(decimal)
        result += char
    return result


#encrypts the code using the XOR-Encryption method, and uses a key that is 23. reason for that is stated in the documentation of the assignment.
def encrypt_binary(binary_string, key):
    key_bin = format(key, '08b')
    encrypted = ''
    for i in range(0, len(binary_string), 8):
        byte = binary_string[i:i+8]
        if len(byte) < 8:
            continue
        encrypted_byte = format(int(byte, 2) ^ int(key_bin, 2), '08b')
        encrypted += encrypted_byte
    
    return encrypted


#simulates packet loss with a 1% likelihood of it happening
def packet_loss(packet, loss_prob = 0.01):
    if random.random() < loss_prob:
        return None
    return packet


#simulates latency that is randomly picked between 5-7 seconds, for reasons that are stated in the documentation of the assignment
def latency():
    time.sleep(random.uniform(5,7))


#this is the first line of defence against binary corruption. 
#basically checks the number of 1s in the binary message, and then if its an odd amount, it makes it an even amount by adding a 1, and if its even then it just adds a 0 to the end of the binary num
def add_parity(binary_string):
    numOfOnes = binary_string.count('1')
    if numOfOnes % 2 == 0 : binary_string = binary_string + '0'
    else: binary_string = binary_string + '1'

    return binary_string


#this is the second layer of error detection. 
#calculates a simple checksum by summing the ASCII values of all characters in the message
def add_checksum(binary_string):
    r = range(0,len(binary_string), 8)
    total = 0 
    for i in r:
        chunk = binary_string[i:i+8]
        total += int(chunk , 2)
    
    checksum_val = total % 256 #to fit in 8 bits
    checksum_binary = format(checksum_val, '08b') #makes the actual value in 8 bits
    result = binary_string + checksum_binary #adds the ascii to the actual binary string
    return result


#parity bits go in pos 1,2,4,8. the rest need to be data bits.
#inserts 8 data bits and 4 parity bits into a 12-bit frame, calculating parity bits based on Hamming rules
def encode_hamming_12_8(byte):
    bits = ['0']*12 #create a list w 12 elements, every element is a 0 at the beginning
    data = list(byte)
    positions = [2, 4, 5, 6, 8, 9, 10, 11]
    for i in range(8):
        bits[positions[i]] = data[i]

    p1 = (int(bits[2]) + int(bits[4]) + int(bits[6]) + int(bits[8]) + int(bits[10])) % 2
    bits[0] = str(p1) #first parity bit in position 0
    p2 = (int(bits[2]) + int(bits[5]) + int(bits[6]) + int(bits[9]) + int(bits[10])) % 2
    bits[1] = str(p2)#second parity bit in position 1
    p4 = (int(bits[4]) + int(bits[5]) + int(bits[6]) + int(bits[11])) % 2
    bits[3] = str(p4)#third parity bit in position 3
    p8 = (int(bits[8]) + int(bits[9]) + int(bits[10]) + int(bits[11])) % 2
    bits[7] = str(p8)#forht parity bit in position 7
    return ''.join(bits)


#randomly flips a specified number of bits in the binary message to simulate corruption.
def corrupt_binary(binary_string, num_flips):
    # if there's nothing to corrupt or num_flips is invalid, just return the original
    if not binary_string or num_flips is None or num_flips < 1:
        return binary_string

    binary_list = list(binary_string)
    string_length = len(binary_list)

    # ensure we don't try to flip more bits than the string contains
    num_flips = min(num_flips, string_length)

    for _ in range(num_flips):
        bit = random.randint(0, string_length - 1)
        binary_list[bit] = '1' if binary_list[bit] == '0' else '0'

    return ''.join(binary_list)


#flips individual bits in the binary message based on a probability
def corruption(binary_string, error_rate = 0.001):
    corrupted = []
    for bit in binary_string:
        if random.random() < error_rate:
            if bit == '0':
                corrupted.append('1')
            else: 
                corrupted.append('0')
        else:
            corrupted.append(bit)
    return ''.join(corrupted)


#randomly selects an astronaut or a rover, generates an emergency type, and displays a warning
#logs the emergency in system_status
def simulate_emergency():
    people = []

    for i in range(1, 5):
        people.append(("Astronaut-" + str(i), GNSS_Symulation.astronauts[i - 1]))

    for i in range(1, 17):
        people.append(("Rover-" + str(i), GNSS_Symulation.rovers[i - 1]))

    sender, pos = random.choice(people)
    is_rover = "Rover" in sender

    #emergency types
    astro_emergencies = [
        "Toxic gas detected",
        "Vital signs unstable",
        "Oxygen level critical",
        "Helmet damage detected",
        "Extreme temperature detected"
    ]

    rover_emergencies = [
        "Toxic gas detected",
        "Signal lost (no contact for 60 seconds)",
        "Rover flipped over",
        "Obstacle collision",
        "Sensor offline"
    ]

    if is_rover:
        emergency_type = random.choice(rover_emergencies)
    else:
        emergency_type = random.choice(astro_emergencies)

    rounded_pos = (round(pos[0], 2), round(pos[1], 2))

    print("\033[91m")  # red

    if is_rover:
        print(f"[Rover Emergency] {sender} detected {emergency_type.lower()} at {rounded_pos}")
    else:
        print("!!!DISTRESS SIGNAL RECEIVED!!!")
        print(f"{sender} at {rounded_pos}")
        print(f"Emergency Type: {emergency_type}")

        min_distance = float("inf")
        nearest_astro = None

        for other_id in range(1, 5):
            name = f"Astronaut-{other_id}"
            if name == sender:
                continue  # skip self
            pos_other = GNSS_Symulation.astronauts[other_id - 1]
            dx = pos_other[0] - pos[0]
            dy = pos_other[1] - pos[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < min_distance:
                min_distance = dist
                nearest_astro = name

        print(f"{nearest_astro} is en route to assist {sender} at {rounded_pos}. Estimated distance: {round(min_distance, 1)} meters.")

    print("\033[0m")

    system_status[sender]["status"] = "emergency"
    system_status[sender]["emergency_type"] = emergency_type


#requests a sender's status and emergency type from system_status and restores them to normal instead of emergency
def clear_emergency(sender_name):
    if sender_name in system_status:
        system_status[sender_name]["status"] = "normal"
        system_status[sender_name]["emergency_type"] = None


#decrypts the message by applying XOR w the same 23 key. since XOR is symmetrical you just need to call the function again
def decrypt_binary(binary_string, key):
    return encrypt_binary(binary_string, key)


#counts the number of 1s in the binary message after corruption, and checks if the number of 1s is odd or even
#indicates corruption if odd
def check_parity(binary_string):
    numOfOnes = binary_string.count('1')
    if numOfOnes % 2 == 0 : 
        return "no corruption found"
    else: 
        return "corrupted"
    

#separates the parity bit from the data, recalculates what the parity should be and checks if it matches
def verify_parity(byte_with_parity):
    """Verifies parity of a 9-bit byte with the last bit as the parity bit."""
    data = byte_with_parity[:-1]
    parity_bit = byte_with_parity[-1]
    expected_parity = '0' if data.count('1') % 2 == 0 else '1'
    return parity_bit == expected_parity


#separates the last 8 bits as the checksum, recalculates the checksum from the data and checks if they match
def check_checksum(binary_string):
    message = binary_string[:-8] #message w out the checksum
    checksum = binary_string[-8:] #checksum that was attached to the message
    total = 0 
    r = range(0, len(message), 8)
    for i in r:
        chunk = message[i:i+8]
        total += int(chunk, 2)

    result = format(total % 256 , '08b') #calculated checksum
    if result == checksum:
        return "no corruption found"
    else:
        return "corrupted"


#will take a 12-bit hamming included string, turn into list to edit it
#recalculate all 4 parity bits to find the one where the flip happened
#flip the messed up bit, and extract the og (fixed) message.
def decode_hamming_12_8(bits):
    
    if len(bits) != 12:
        return None
    
    bits = list(bits)
    error_pos = 0 #helps track error position
    #correct p's
    correct_p1 = (int(bits[2]) + int(bits[4]) + int(bits[6]) + int(bits[8]) + int(bits[10])) % 2
    correct_p2 = (int(bits[2]) + int(bits[5]) + int(bits[6]) + int(bits[9]) + int(bits[10])) % 2
    correct_p4 = (int(bits[4]) + int(bits[5]) + int(bits[6]) + int(bits[11])) % 2
    correct_p8 = (int(bits[8]) + int(bits[9]) + int(bits[10]) + int(bits[11])) % 2
    
    #real p's
    real_p1 = int(bits[0])
    real_p2 = int(bits[1])
    real_p4 = int(bits[3])
    real_p8 = int(bits[7])

    #if loops:
    if correct_p1 != real_p1: 
        error_pos += 1
    if correct_p2 != real_p2 :
        error_pos += 2
    if correct_p4 != real_p4 :
        error_pos += 4
    if correct_p8 != real_p8 :
        error_pos += 8

    #fix the current problem w indexes:
    if error_pos < 1 or error_pos > len(bits):
        return None

    #fixing part of hamming by flipping the bit at the index where the error was calculated:
    if error_pos > 0:
        if bits[error_pos - 1] == '0':
            bits[error_pos - 1] ='1'
        elif bits[error_pos - 1] == '1':
            bits[error_pos - 1] ='0'

    #putting things back together after they got fixed:
    result = []
    for i in [2,4,5,6,8,9,10,11]:
        result.append(bits[i])  
    return ''.join(result)


#this function handles the entire process of sending a message and retrying if it fails to send(either too much corruption for hamming to fix, or decryption doesnt make the message proper)
#if encryption is requested by the user:
#   the binary is split into 8 bit chunks, each encoded with Hamming
#   these encoded blocks are sent and might get corrupted during transmission, every bit in the block has a chance
#   the system tries to fix and collect valid blocks over many retries, it is kind of like building the message up brick by brick
#   already recovered blocks are skipped in future retries to reduce the number of retries
#   once all the blocks are recovered, and the text is actually what it should be, the binary is decrypted and converted back to text
#if encryption is off:
#   the whole message is sent with an added checksum.
#   the receiver checks if the checksum matches to verify if the message matches the original message(basically to check if the corruption has been corrected).
#if transmission is successful:
#   the recovered message is printed and saved to the transmission log.
#if the max number of retries are reached:
#   the message is marked as failed but still logged.
def resend_with_retries(binary_string, original_user_text, original_binary, max_retries=50, encryption_used=False, emergency_override=False, message_id=1, sender_name=None, sender_position=None):
    tries = 0
    start_time = time.time()
    msg = ""
    latency()  # simulate latency once per transmission

    # Set retry limit
    if encryption_used:
        max_retries = 500

    # Split message into 8-bit chunks for Hamming
    block_count = len(binary_string) // 8
    recovered_blocks = [None] * block_count

    while tries < max_retries:
        tries += 1
        hamming_encoded = []
        sent_block_indices = []

        for i in range(block_count):
            if recovered_blocks[i] is not None:
                continue
            byte = binary_string[i*8:(i+1)*8]
            if len(byte) < 8:
                continue
            hamming_block = encode_hamming_12_8(byte)
            hamming_encoded.append(hamming_block)
            sent_block_indices.append(i)

        if not hamming_encoded:
            break

        msg = ''.join(hamming_encoded)
        corrupted = corruption(msg, error_rate=0.001)
        corrupted = corrupt_binary(corrupted, num_flips=1)
        packet = packet_loss(corrupted, loss_prob=0.005)

        if packet is None:
            if tries == 1:
                print("Packet loss, retrying...")
            continue

        pointer = 0
        for block_index in sent_block_indices:
            block = packet[pointer:pointer+12]
            pointer += 12
            decoded = decode_hamming_12_8(block)
            if decoded and len(decoded) == 8:
                recovered_blocks[block_index] = decoded

        if None not in recovered_blocks:
            recovered_binary = ''.join(recovered_blocks)

            # Make sure recovered binary is a multiple of 8
            if len(recovered_binary) % 8 != 0:
                if tries == 1:
                    print("Recovered binary length mismatch, retrying...")
                continue

            # Decode final message
            if encryption_used:
                decrypted = decrypt_binary(recovered_binary, 23)
                recovered_text = binary_into_text(decrypted)
            else:
                recovered_text = binary_into_text(recovered_binary)

            end_time = time.time()
            latency_seconds = round(end_time - start_time, 2)

            print_transmission_success(clean_output(recovered_text), emergency_override, tries, sender_name, sender_position)

            log_transmission(
                message_id=message_id,
                attempts=tries,
                encryption_used=encryption_used,
                emergency_override=emergency_override,
                success=True,
                encrypted_message=msg,
                sender_name=sender_name,
                sender_position=sender_position,
                latency=latency_seconds,
                final_message = clean_output(recovered_text)
            )
            return tries

    # if all retries fail
    end_time = time.time()
    latency_seconds = round(end_time - start_time, 2)
    print("Transmission failed after", max_retries, "attempts.")

    log_transmission(
        message_id=message_id,
        attempts=tries,
        encryption_used=encryption_used,
        emergency_override=emergency_override,
        success=False,
        encrypted_message=msg,
        sender_name=sender_name,
        sender_position=sender_position,
        latency=latency_seconds,
        final_message="N/A"
    )
    return tries


# starts a loop where the user can send messages, the loop simulates emergencies, and the user can view system info
# first, the user selects a sender (astronauts 1-4) and their position is imported from the GNSS_Symulation file
# the loop listens for specific messages from the sender:
#   typing a normal message triggers the binary encoding and the transmission process
#   commands like emergency, log, positions, etc. trigger specific actions (toggling modes, showing info, saving logs)
#   if encryption is toggled on, the message is encrypted before sending
# the message is sent using resend_with_retries, which handles error correction and retry logic
# after each message, there's a small chance the system automatically triggers a random emergency(at this time it is 3%, but for testing purposes it can be changed)
# the loop continues until the user types exit or quit
def start_loop():
    global message_counter
    global emergency_mode
    global encryption_mode

    print("Lunar Communications System Initiated")
    print("\nSelect sender:")
    print("1: Astronaut-1\n2: Astronaut-2\n3: Astronaut-3\n4: Astronaut-4")

    try:
        sender_id = int(input("Enter sender ID (1-4): ").strip())  
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    if sender_id not in range(1, 5):
        print("Invalid sender ID. Try again.")
        return

    sender_name = f"Astronaut-{sender_id}"
    sender_position = GNSS_Symulation.astronauts[sender_id - 1]

    print("Type your message, or type: ")
    print("'emergency' to activate emergency mode")
    print("'encryption' to toggle encryption mode")
    print("'change sender' to change the sender (astronaut/rover)")
    print("'positions' to see the positions of the habitat, beacons, astronauts, and rovers")
    print("'log' to see past transmissions")
    print("'distance <astronaut-X/rover-X/habitat/beacon-X>' to check the distance between the sender and the target")
    print("'exit' to end the session")

    while True:
        user_input = input("Message: ")

        if user_input.lower().strip() in ["exit", "quit"]:
            print("\nSession Ended.")
            break

        elif user_input.lower().strip() == "log":
            print("type 'save' to save this log to the logs of data.")
            show_log()
            continue

        elif user_input.lower().strip() == "emergency":
            emergency_mode = True
            print("Emergency mode activated, to go back to normal mode, type 'normal'.")
            continue

        elif user_input.lower().strip() == "normal":
            emergency_mode = False
            print("Emergency mode deactivated.")
            continue

        elif user_input.lower().strip() == "save":
            save_log()
            continue

        elif user_input.lower().strip() == "show beacons":
            GNSS_Symulation.show_beacons()
            continue

        elif user_input.lower().strip() == "encryption":
            encryption_mode = True
            print("Encryption mode activated. Messages will now be encrypted.")
            print("If you want encryption mode to be turned off, type: 'encryption off'")
            continue

        elif user_input.lower().strip() == "encryption off":
            encryption_mode = False
            print("Encryption mode deactivated. Messages will now be sent without encryption.")
            continue

        elif user_input.lower().strip() == "simulate emergency":
            simulate_emergency()
            continue

        elif user_input.lower().strip() == "positions":
            GNSS_Symulation.show_positions()
            continue

        elif user_input.lower().startswith("where "):
            target = user_input[6:].lower().strip()

            if target.startswith("astronaut-"):
                try:
                    astro_num = int(target.split("-")[1])
                    pos = GNSS_Symulation.astronauts[astro_num -1]
                    print(f"{target.capitalize()} is at {round(pos[0],1)}, {round(pos[1],1)}")
                except (IndexError, ValueError):
                    print("Invalid Astronaut ID.")

            elif target.startswith("rover-"):
                try:
                    rover_num = int(target.split("-")[1])
                    pos = GNSS_Symulation.rovers[rover_num -1]
                    print(f"{target.capitalize()} is at {round(pos[0],1)}, {round(pos[1],1)}")
                except (IndexError, ValueError):
                    print("Invalid rover ID.")
            else:
                print("Invalid format. Use 'where astronaut-1' or 'where rover-5'.")
            continue

        elif user_input.lower().startswith("distance "):
            target = user_input[9:].lower().strip()

            if target.startswith("astronaut-"):
                try:
                    astro_num = int(target.split("-")[1])
                    target_pos = GNSS_Symulation.astronauts[astro_num -1]
                except (IndexError, ValueError):
                    print("Invalid astronaut ID.")
                    continue

            elif target.startswith("rover-"):
                try:
                    rover_num = int(target.split("-")[1])
                    target_pos = GNSS_Symulation.rovers[rover_num - 1]
                except (IndexError, ValueError):
                    print("Invalid rover ID.")
                    continue

            elif target == "habitat":
                target_pos = GNSS_Symulation.habitat_pos

            elif target.startswith("beacon-"):
                try:
                    beacon_id = int(target.split("-")[1])
                    if 1 <= beacon_id <= len(GNSS_Symulation.beacon_pos):
                        target_pos = GNSS_Symulation.beacon_pos[beacon_id - 1]
                    else:
                        print("Beacon number out of range.")
                        continue
                except:
                    print("Invalid beacon ID format")
                    continue
            else:
                print("Invalid format. Use 'distance astronaut-1' or 'distance rover-5'.")
                continue

            dx = target_pos[0] - sender_position[0]
            dy = target_pos[1] - sender_position[1]
            distance = round((dx**2 + dy**2)**0.5, 1)
            print(f"Distance from {sender_name} to {target.capitalize()} is {distance} meters.")
            continue

        elif user_input.lower().strip() == "change sender":
            print("\nSelect new sender:")
            print("1: Astronaut-1\n2: Astronaut-2\n3: Astronaut-3\n4: Astronaut-4")
            try:
                sender_id = int(input("Enter new sender ID (1-4): ").strip())
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if sender_id not in range(1, 5):
                print("Invalid sender ID. Try again.")
                continue

            sender_name = f"Astronaut-{sender_id}"
            sender_position = GNSS_Symulation.astronauts[sender_id - 1]
            print(f"Sender changed to {sender_name} at position {sender_position}")
            continue

        if "Astronaut" in sender_name:
            GNSS_Symulation.update_astro_pos()
            sender_position = GNSS_Symulation.astronauts[sender_id -1]

        original_binary = text_into_binary(user_input)

        if encryption_mode:
            prepared_binary = encrypt_binary(original_binary, 23)
        else:
            prepared_binary = add_checksum(original_binary)

        resend_with_retries(
            prepared_binary,
            original_user_text=user_input,
            original_binary=original_binary,
            encryption_used=encryption_mode,
            emergency_override=emergency_mode,
            message_id=message_counter,
            sender_name=sender_name,
            sender_position=sender_position
        )

        message_counter += 1

        if random.random() < 0.03:
            print("\n\033[93m[!] Automatic emergency triggered...\033[0m")
            simulate_emergency()



#interactive transmission function, asks the user for a message, and then transforms it into binary
#increments the global message counter after each successful or failed attempt
def send_message():
    global message_counter
    user_message = input("Write your message here: ")
    binary_message = text_into_binary(user_message)

    resend_with_retries(binary_message, 
                        encryption_used= True, 
                        emergency_override = emergency_mode, 
                        message_id = message_counter)
    
    message_counter += 1


start_loop()
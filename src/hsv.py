import micropython

def norm_hsv(hsv):

    ''' Turns an HSV tuple with H in degrees and SV in percent into byte normalized form '''

    H, S, V = hsv
    result = (int(H / 360 * 255), int(S / 100 * 255), int(V / 100 * 255))
    # print("turning ", H, S, V, " into ", *result)
    return result

@micropython.viper
def hsv_rgb(hsv_bytes_obj, rgb_bytes_obj, in_start: int, out_start: int, reverse: bool):

    ''' Converts an integer HSV tuple (value range from 0 to 255) to an RGB tuple '''

    hsv_bytes = ptr8(hsv_bytes_obj)
    rgb_bytes = ptr8(rgb_bytes_obj)
    # order = bytes((1, 0, 2))

    num_vals = (int(len(hsv_bytes_obj)) - in_start) // 3

    max_in_idx = (num_vals - 1) * 3 + 2 + in_start
    hsv_len = int(len(hsv_bytes_obj))
    if max_in_idx > hsv_len:
        print("max_in_idx: ", max_in_idx, " hsv_len: ", hsv_len, " num_vals: ", num_vals)
        raise Exception("Bad values!")

    for i in range(0, num_vals):
        H = hsv_bytes[i * 3 + in_start]
        S = hsv_bytes[i * 3 + 1 + in_start]
        V = hsv_bytes[i * 3 + 2 + in_start]

        # Check if the color is Grayscale
        if S == 0:
            if reverse:
                base = ((num_vals - 1) * 3) - i * 3 + out_start
                rgb_bytes[base + 1] = V
                rgb_bytes[base + 0] = V
                rgb_bytes[base + 2] = V
            else:
                rgb_bytes[i * 3 + 1 + out_start] = V
                rgb_bytes[i * 3 + 0 + out_start] = V
                rgb_bytes[i * 3 + 2 + out_start] = V
            continue

        # Make hue 0-5
        region = H // 43;

        # Find remainder part, make it from 0-255
        remainder = (H - (region * 43)) * 6; 

        # Calculate temp vars, doing integer multiplication
        P = (V * (255 - S)) >> 8;
        Q = (V * (255 - ((S * remainder) >> 8))) >> 8;
        T = (V * (255 - ((S * (255 - remainder)) >> 8))) >> 8;


        # Assign temp vars based on color cone region
        if region == 0:
            R = V
            G = T
            B = P

        elif region == 1:
            R = Q
            G = V
            B = P

        elif region == 2:
            R = P
            G = V
            B = T

        elif region == 3:
            R = P
            G = Q
            B = V

        elif region == 4:
            R = T
            G = P
            B = V

        else: 
            R = V
            G = P
            B = Q
        if reverse:
            base = ((num_vals - 1) * 3) - i * 3 + out_start
            rgb_bytes[base + 1] = R
            rgb_bytes[base + 0] = G
            rgb_bytes[base + 2] = B
        else:
            rgb_bytes[i * 3 + 1 + out_start] = R
            rgb_bytes[i * 3 + 0 + out_start] = G
            rgb_bytes[i * 3+ 2 + out_start] = B

@micropython.viper
def hsv_rgb_tup(hsv):

    ''' Converts an integer HSV tuple (value range from 0 to 255) to an RGB tuple '''
    # order = bytes((1, 0, 2))

    H = int(hsv[0])
    S = int(hsv[1])
    V = int(hsv[2])

    # Check if the color is Grayscale
    if S == 0:
        return (V, V, V)

    # Make hue 0-5
    region = H // 43;

    # Find remainder part, make it from 0-255
    remainder = (H - (region * 43)) * 6; 

    # Calculate temp vars, doing integer multiplication
    P = (V * (255 - S)) >> 8;
    Q = (V * (255 - ((S * remainder) >> 8))) >> 8;
    T = (V * (255 - ((S * (255 - remainder)) >> 8))) >> 8;


    # Assign temp vars based on color cone region
    if region == 0:
        R = V
        G = T
        B = P

    elif region == 1:
        R = Q
        G = V
        B = P

    elif region == 2:
        R = P
        G = V
        B = T

    elif region == 3:
        R = P
        G = Q
        B = V

    elif region == 4:
        R = T
        G = P
        B = V

    else: 
        R = V
        G = P
        B = Q
        
    return (R, G, B)

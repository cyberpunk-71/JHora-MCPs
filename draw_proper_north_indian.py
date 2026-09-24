def draw_north_indian_box(title, lagna_sign_num, house_data):
    # house_data: dict of house_num (1 to 12) -> (sign_num, list_of_planets)
    # Signs: 1=Ar, 2=Ta, 3=Ge, 4=Cn, 5=Le, 6=Vi, 7=Li, 8=Sc, 9=Sg, 10=Cp, 11=Aq, 12=Pi
    
    # House layout:
    # H1: Top Center Diamond
    # H2: Top Left Triangle
    # H3: Left Top Triangle
    # H4: Left Center Diamond
    # H5: Left Bottom Triangle
    # H6: Bottom Left Triangle
    # H7: Bottom Center Diamond
    # H8: Bottom Right Triangle
    # H9: Right Bottom Triangle
    # H10: Right Center Diamond
    # H11: Right Top Triangle
    # H12: Top Right Triangle
    
    def p_str(h):
        s_num, plist = house_data[h]
        p_txt = " ".join(plist) if plist else ""
        return f"{s_num} {p_txt}".strip()
    
    print(f"\n+=============================================================================+")
    print(f"| {title.center(75)} |")
    print(f"+=============================================================================+")
    print(f"| \\                 / \\                 /|\\                 / \\                 / |")
    print(f"|   \\    H2: {p_str(2):<6}   /     \\     H1: {p_str(1):<6}   / | \\    H1: {p_str(1):<6}   /     \\   H12: {p_str(12):<6}   /   |")
    print(f"|     \\           /         \\           /  |  \\           /         \\           /     |")
    print(f"|       \\       /             \\       /    |    \\       /             \\       /       |")
    print(f"|  H3:    \\   /                 \\   /      |      \\   /                 \\   /   H11:  |")
    print(f"|  {p_str(3):<6}  \\ /     LAGNA: {p_str(1):<6} \\ /       |       \\ /     LAGNA: {p_str(1):<6} \\ /    {p_str(11):<6} |")
    print(f"|----------X---------------------X---------|---------X---------------------X----------|")
    print(f"|  H4:    / \\                   / \\        |        / \\                   / \\   H10:  |")
    print(f"|  {p_str(4):<6}/   \\                 /   \\       |       /   \\                 /   \\  {p_str(10):<6} |")
    print(f"|       /       \\             /       \\    |    /       \\             /       \\       |")
    print(f"|     /           \\         /           \\  |  /           \\         /           \\     |")
    print(f"|   /    H5: {p_str(5):<6}   \\     /     H7: {p_str(7):<6}   \\ | /    H7: {p_str(7):<6}   \\     /    H9: {p_str(9):<6}   \\   |")
    print(f"| /                 \\   /                 \\|/                 \\   /                 \\ |")
    print(f"|---------------------X--------------------|--------------------X---------------------|")
    print(f"| \\                 /   \\                 /|\\                 /   \\                 / |")
    print(f"|   \\    H6: {p_str(6):<6} /     \\     H7: {p_str(7):<6} / | \\     H7: {p_str(7):<6} /     \\    H8: {p_str(8):<6} /   |")
    print(f"|     \\           /         \\           /  |  \\           /         \\           /     |")
    print(f"+------------------------------------------+------------------------------------------+")


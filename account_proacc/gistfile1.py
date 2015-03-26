def checksum(number):
    """
    Create a valid betalingskenmerk for the Dutch rabobank.

    Generates a 16 digit number for the number received. The number should be a 15 digit long string.
    There are no checks to validate the number.

    :param number: String of numbers to convert to valid betalingskenmerk
    :return: 16 digit long string with a valid betalingskenmerk
    """

    # First, pad the number with zeroes:
    number = (15 - len(number)) * '0' + number

    # Multiply the numbers from right to left with the repeating range: 2, 4, 8, 5, 10, 9, 7, 3, 6, 1
    # (Yes, this is the non-pythonic way, but it works.
    weightedsum = 0
    weightedsum += int(number[14]) * 2
    weightedsum += int(number[13]) * 4
    weightedsum += int(number[12]) * 8
    weightedsum += int(number[11]) * 5
    weightedsum += int(number[10]) * 10
    weightedsum += int(number[9]) * 9
    weightedsum += int(number[8]) * 7
    weightedsum += int(number[7]) * 3
    weightedsum += int(number[6]) * 6
    weightedsum += int(number[5]) * 1
    weightedsum += int(number[4]) * 2
    weightedsum += int(number[3]) * 4
    weightedsum += int(number[2]) * 8
    weightedsum += int(number[1]) * 5
    weightedsum += int(number[0]) * 10

    # Generate checksum digit
    controlegetal = 11 - (weightedsum % 11)
    if controlegetal == 10:
        controlegetal = '1'
    elif controlegetal == 11:
        controlegetal = '0'
    else:
        controlegetal = str(controlegetal)

    number = ''.join((controlegetal, number))
    return number

test = [('547165445', '1000000547165445'),
        ('499492307', '9000000499492307'),
        ('194283237918941', '2194283237918941'),
        ('194283237918941', '2194283237918941'),
        ('166044737023032', '2166044737023032')]

for testnumber in test:
    print "Input     : ", str(testnumber[0]).rjust(16, ' ')
    print "Exptected : ", str(testnumber[1]).rjust(16, ' ')
    print "Real      : ", str(checksum(testnumber[0])).rjust(16, ' ')
    if testnumber[1] == checksum(testnumber[0]):
        print "Hooray, Match!"
    else:
        print "Such a shame, no match"


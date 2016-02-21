__author__ = 'zacharywwilson'

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


#####################
#       CONFIG      #
#####################
# This is the only config that needs to be done
BORDER_COLOR = (232,232,232) # What color (RBG) to be looking for as a border
BORDER_SIZE = 20 # How large (in pixels) is the border - prevents false positives
FONT_SIZE = 16 # How large (in pixels) the ID should be displayed on the overlay
MIN_POST_SIZE = 250 # How large (in pixels) the smallest post is. (To prevent false positives from headers/footers)

#####################
#     END CONFIG    #
#####################


####################
# Helper Functions #
####################

# Puts a number ID on the photo
def writeID(x,y,id,draw, fontSize):

    # Does the setup
    id = str(id)
    font_color = (0,0,0)
    shadow_color = (255,255,255)
    f = ImageFont.truetype("Arimo-Bold.ttf",fontSize) # Arimo-Bold should be included in the package

    # Draws the white thin border around text (For contrast against images)
    draw.text((x-1, y), id, font=f, fill=shadow_color)
    draw.text((x+1, y), id, font=f, fill=shadow_color)
    draw.text((x, y-1), id, font=f, fill=shadow_color)
    draw.text((x, y+1), id, font=f, fill=shadow_color)

    # Draws the actual foreground image
    draw.text((x,y),id,font_color,font=f)

    # Returns the draw object with current additions
    return draw

# Writes the created reference array to excel
def write2xlsx(fp, a):
    import xlsxwriter

    # Splits out the .png on the filepath
    output = fp.split('.')
    output = output[0]

    # Creates the workbook and worksheet (Workbook is the picture name with _MAP on the end)
    workbook = xlsxwriter.Workbook(output+'_MAP.xlsx')
    worksheet = workbook.add_worksheet()

    # Writes the data to the excel file
    row = 0
    for col, data in enumerate(a):
        worksheet.write_column(row, col, data)

    # Closes file
    workbook.close()

#######################
#        MAIN         #
#######################

# Since these files tend to be large, expands max pixels to prevent errors/warnings
Image.MAX_IMAGE_PIXELS = None
print "\nWelcome to the Pinterest Image Network Survey (PINS). This will \nanalyze how many pins are in an image. Please make sure everything \nis configured properly and file is in image format (JPG or PNG).\n"

# Needed information for file run
filepath = raw_input("Please enter the full filepath: ")
filename = raw_input("Please enter the file name: ")
num_columns = raw_input("Please enter the number of columns: ")
id_photos = raw_input("Would you like to mark photos with ID? (y/n): ")

# Makes sure the file path is correct
if (filepath[-1:] != "/"):
    filepath += "/"

# Converts id_photos to True/False boolean value
id_photos = id_photos.lower()
if id_photos[0] == "y" or id_photos[0] == "t":
    id_photos = True
else:
    id_photos = False

# Imports image using PIL (PILLOW)
im =  Image.open(filepath+filename)
im = im.convert("RGB")
width, height = im.size

# Creates draw
draw = ImageDraw.Draw(im)


# Calculates the column width in pixels
num_columns = int(num_columns)
column_width = int(width/(num_columns))

# Initializes needed variables & counters
unique_counter = 0
photo_found = False
arr = []

for i in range(0, num_columns):

    # Resets needed counters with each row
    border_counter = 0
    row_counter = 0
    false_positive_counter = 0
    top_center_id = None


    for j in range(0,height):

        # Gets the pixel color
        r,g,b = im.getpixel((int(i * column_width + 0.5 * column_width),j))

        # If the pixel matches border color
        if (r == BORDER_COLOR[0] and g == BORDER_COLOR[1] and b == BORDER_COLOR[2]):
            border_counter += 1


            # If a border is found, resets photo_found to false
            if (border_counter == BORDER_SIZE):
                false_positive_counter = 0
                photo_found = False

        # If the pixel is outside of border color
        else:
            border_counter = 0
            false_positive_counter += 1

            # Handles new photo. Increments counters & possibly adds a small label
            if photo_found == False and false_positive_counter > MIN_POST_SIZE:
                row_counter += 1
                unique_counter += 1
                photo_found = True

                # If requested, puts a small ID text at the top-center of the photo
                if id_photos:
                    draw = writeID(top_center_id[0],top_center_id[1],unique_counter,draw, FONT_SIZE)

                # Adds location to map array (to be made into excel file)
                arr.append([unique_counter,"("+str(i+1)+","+str(row_counter)+")"])

            if false_positive_counter == min(5,MIN_POST_SIZE-1):
                top_center_id = (int(i * column_width + 0.5 * column_width),j)


# Transposes array so that it writes to excel properly
a = zip(*arr)
write2xlsx(filepath+filename,a)

# Saves new file if IDs are added
if id_photos:
    im.save(filepath+"ID_"+filename)

# Lets the user quickly know how many photos were found
print "\nNumber of photos found: " + str(unique_counter)
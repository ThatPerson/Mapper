from PIL import Image


### Read topography

filename = "map1.png"

a = Image.open(filename)
p = a.load()

siz = a.size

#158 242

topography = [[0 for i in xrange(siz[1])] for j in xrange(siz[0])]


print(siz)
for x in range(0, siz[1]):

    st = ""
    for y in range(siz[0]-1, 0, -1):
        ar = p[y, x]
        height = ar[2]*10
        topography[y][x] = height
        #print(str(x) + ", " + str(y) + ", " + str(height))


def cross(v_a, v_b):
    return [v_a[1] * v_b[2] - v_a[2]*v_b[1], v_a[2]*v_b[0] - v_a[0]*v_b[2], v_a[0]*v_b[1] - v_a[1]*v_b[0]]

class Bed:
    def __init__(self, points, thickness, faults_above, faults_below, z_index, colour):
        self.points = points
        self.thickness = thickness # Thickness above points. If this is the top surface make negative.
        self.get_indices()
        self.bounding_faults_top = faults_above
        self.bounding_faults_bottom = faults_below
        self.z = z_index # If the point is in two units then take the highest z-index - ie, an unconformity.
        self.colour = colour
    def get_indices(self):
        if (len(self.points)<3):
            print("Insufficient Points")
            return 0
        v_a = [self.points[1][0] - self.points[0][0], self.points[1][1] - self.points[0][1], self.points[1][2] - self.points[0][2]]
        v_b = [self.points[2][0] - self.points[0][0], self.points[2][1] - self.points[0][1], self.points[2][2] - self.points[0][2]]
        normal = cross(v_a, v_b)
        if (normal[2] < 0):
            normal[0] = -normal[0]
            normal[1] = -normal[1]
            normal[2] = -normal[2]
        normal.append(normal[0]*self.points[0][0] + normal[1]*self.points[0][1] + normal[2]*self.points[0][2])
        self.indices = normal
    def is_point_below(self,point):
        z_bed = (self.indices[3] - self.indices[0]*point[0] - self.indices[1]*point[1])/(self.indices[2])
        if (point[2] <= z_bed):
            return 1
        return 0
    def is_point_inside(self, point):
        z_bed = (self.indices[3] - self.indices[0]*point[0] - self.indices[1]*point[1])/(self.indices[2])
        z_top = z_bed + self.thickness
        if ((z_bed <= point[2] and point[2] <= z_top) or (z_top <= point[2] and point[2] <= z_bed)):
            return 1
        return 0

beds = []
faults = []

faults.append(Bed([[81,0,100], [117,0,500], [145,175,500]], -50, [], [], 9, [0,0,1]))

#beds.append(Bed([[220,140,400], [201,145, 300], [182, 151, 200]], 50, [0], [], 9, [0,0,0])) ### DYKE E
#beds.append(Bed([[220,60,400], [201,65, 300], [182, 71, 200]], 50, [], [0], 9, [0,0,0])) #### Dyke W

beds.append(Bed([[31,37, 300], [58, 107,300], [20, 148, 100]], -98, [0],[],1, [1,0,0])) # W

beds.append(Bed([[31,37, -200], [58, 107,-200], [20, 148, -400]], -98, [],[0],1, [0,1,0])) # E

beds.append(Bed([[131, 0, 300], [55, 0, 450], [159, 57, 450]], 700, [],[],4, [0.44, 0.4,0]))

z = 300

x = 50
y = 60

upper_x = 160
upper_y = 242

def get_unit(point):
    current_zindex = 0
    current_unit = -1
    q = 0
    for i in range(0, len(beds)):
        q = 0
        if (beds[i].is_point_inside(point) == 1):
            for p in beds[i].bounding_faults_top:
                if (faults[p].is_point_below(point) == 1):
                    q = 1
            for p in beds[i].bounding_faults_bottom:
                if (faults[p].is_point_below(point) != 1):
                    q = 1
            if (beds[i].z > current_zindex and q == 0):
                #Then this is our unit
                current_zindex = beds[i].z
                current_unit = i
    return current_unit


def image_over_z(z, topographyr, filename):
    img = Image.new( 'RGB', (len(topography),len(topography[0])), "black") # create a new black image
    pixels = img.load() # create the pixel map
    for x in range(0, len(topography)):
        for y in range(0, len(topography[0])):
            if (topographyr == 1):
                z = topography[x][y]
            print(z)
            qw = get_unit([x, 242-y, z-2])

            qwer = beds[qw].colour
            if (qw == -1):
                qwer = [1, 1, 1]
            pixels[x, y] = (int(qwer[0]*255*2*z/800), int(qwer[1]*255*2*z/800), int(qwer[2]*255*2*z/800))

    img.save(filename)


def image_over_y(y, filename):
    img = Image.new( 'RGB', (len(topography),100), "black") # create a new black image
    pixels = img.load() # create the pixel map
    for x in range(0, len(topography)):
        for z in range(0, 100):
            if (z*10 <= topography[x][y]):
                qw = get_unit([x, y, z*10])
                qwer = beds[qw].colour
                if (qw == -1):
                    qwer = [1, 1, 1]
                pixels[x, 99-z] = (int(qwer[0]*255), int(qwer[1]*255), int(qwer[2]*255))
            else:
                pixels[x, 99-z] = (255, 255, 255)



    img.save(filename)

#image_over_y(241, "example.png")
image_over_z(270, 1, "example.png")
print("The point "+str(x)+", "+str(y)+", "+str(z)+" is within unit "+str(get_unit([x, y, z])))

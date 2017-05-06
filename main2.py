from PIL import Image
import math

### Read topography

filename = "map.png"

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
        topography[y][x] = height *(47/500)
        #print(str(x) + ", " + str(y) + ", " + str(height))


def cross(v_a, v_b):
    return [v_a[1] * v_b[2] - v_a[2]*v_b[1], v_a[2]*v_b[0] - v_a[0]*v_b[2], v_a[0]*v_b[1] - v_a[1]*v_b[0]]
def magnitude(v):
    x = 0
    for i in v:
        x = x + pow(i,2)
    return math.sqrt(x)
def dot(v_a, v_b):
    x = 0
    if (len(v_a) != len(v_b)):
        print ("Vectors not the same length")
        return 0

    for i in range(0, len(v_a)):
        x = x + v_a[i]*v_b[i]
    return x

class Bed:
    def __init__(self, name, points, thickness, faults_above, faults_below, z_index, colour):
        self.points = points
        self.name = name
        self.thickness = thickness # Thickness above points. If this is the top surface make negative.
        self.get_indices()

        self.dip = 0
        self.strike = 0
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
    def get_orientation(self):
        #a.b = |a||b|cosx
        #x = acos((a.b)/(|a||b|))
        self.dip = int(90-round((180/math.pi)*math.acos(dot(self.indices[:3], [0, 0, 1])/magnitude(self.indices[:3]))))
        self.strike = 0
        mag = magnitude(self.indices[:3])
        print(str(self.indices[0]/mag) + ", "+str(self.indices[1]/mag)+", "+str(self.indices[2]/mag))
        # let x = 0, 100. z = 100. Calculate y. Use atan(y/100)
        if (self.indices[1] == 0):
            return 0
        delta_y = ((self.indices[3] - self.indices[2]*100 - self.indices[0]*0)/self.indices[1]) - ((self.indices[3] - self.indices[2]*100 - self.indices[0]*100)/self.indices[1])
        self.strike = int(90+round((180/math.pi)*math.atan(delta_y/100)))
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

faults.append(Bed("fault", [[159, 81, 100*(47/500)], [0,207, 500*(47/500)], [95,125,200*(47/500)]], 50*(47/500), [], [], 9, [0,0,0]))

beds.append(Bed("Not sure", [[159, 81, 100*(47/500)], [0,207, 500*(47/500)], [95,125,200*(47/500)]], 50*(47/500), [], [], 9, [0,0,0]))

beds.append(Bed("Sandstone W", [[67, 0, 300*(47/500)], [45, 242, 200*(47/500)], [71, 91, 200*(47/500)]], 900*(47/500), [0],[],1, [1,0,0])) # Sandstone
beds.append(Bed("Shale W", [[67, 0, 300*(47/500)], [45, 242, 200*(47/500)], [71, 91, 200*(47/500)]], -300*(47/500), [0],[],1, [0, 0, 1])) # Shale

beds.append(Bed("Sandstone E", [[47, 182, 500*(47/500)], [71, 147, 400*(47/500)], [55, 242, 400*(47/500)]], 900*(47/500), [],[0],1, [1,0,0])) # Sandstone
beds.append(Bed("Shale E", [[47, 182, 500*(47/500)], [71, 147, 400*(47/500)], [55, 242, 400*(47/500)]], -300*(47/500), [],[0],1, [0, 0, 1])) # Shale bounding faults bottom 0

beds.append(Bed("Unconformity W", [[47, 182, 400*(47/500)], [71, 147, 400*(47/500)], [55, 242, 400*(47/500)]], 700*(47/500), [0],[],4, [0.44, 0.4,0])) # Unconformity
beds.append(Bed("Unconformity E", [[47, 182, 600*(47/500)], [71, 147, 600*(47/500)], [55, 242, 600*(47/500)]], 700*(47/500), [],[0],3, [0.44, 0.4,0])) # Unconformity


for i in beds:
    i.get_orientation()
    print(i.name + ":ss "+("{0:0=3d}".format(i.strike))+"/"+("{0:0=2d}".format(i.dip)))


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
print("WORKING")
print(dot([0, 0, 1], [0, 0, 5]))
#image_over_y(241, "example.png")

image_over_z(450, 1, "example.png")

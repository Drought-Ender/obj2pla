import struct, os, math, argparse
from io import BytesIO


class Plane:
    a:float
    b:float
    c:float
    d:float

    def __init__(self, a = 0.0, b = 0.0, c = 0.0, d = 0.0) -> None:
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __str__(self) -> str:
        return f"{self.a}, {self.b}, {self.c}, {self.d}"

    def setVec(self, vec:'Vector3f'):
        self.a = vec.x
        self.b = vec.y
        self.c = vec.z
    
    def getVec(self) -> 'Vector3f':
        return Vector3f(self.a, self.b, self.c)

    def read(self, stream:BytesIO):
        self.a = struct.unpack(">f", stream.read(4))[0]
        self.b = struct.unpack(">f", stream.read(4))[0]
        self.c = struct.unpack(">f", stream.read(4))[0]
        self.d = struct.unpack(">f", stream.read(4))[0]

    def readBackwards(self, stream:BytesIO):
        self.a = struct.unpack("<f", stream.read(4))[0]
        self.b = struct.unpack("<f", stream.read(4))[0]
        self.c = struct.unpack("<f", stream.read(4))[0]
        self.d = struct.unpack("<f", stream.read(4))[0]
    
    def write(self, stream:BytesIO):
        stream.write(struct.pack(">f", self.a))
        stream.write(struct.pack(">f", self.b))
        stream.write(struct.pack(">f", self.c))
        stream.write(struct.pack(">f", self.d))

class Vector3f:
    x:float
    y:float
    z:float
    def __init__(self, *args) -> None:
        if len(args) < 3:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            return
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]

    def flipYZ(self):
        self.y, self.z = self.z, self.y

    def read(self, stream:BytesIO) -> None:
        self.x = struct.unpack(">f", stream.read(4))[0]
        self.y = struct.unpack(">f", stream.read(4))[0]
        self.z = struct.unpack(">f", stream.read(4))[0]

    def write(self, stream:BytesIO):
        stream.write(struct.pack(">f", self.x))
        stream.write(struct.pack(">f", self.y))
        stream.write(struct.pack(">f", self.z))

    def readObj(self, line:str):
        header, x, y, z = line.split()
        assert header == "v"
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def cross_product(self, v2:'Vector3f'):
        cross_x = self.y*v2.z - self.z*v2.y
        cross_y = self.z*v2.x - self.x*v2.z
        cross_z = self.x*v2.y - self.y*v2.x
        return Vector3f(cross_x, cross_y, cross_z)
    
    def dot(self, vec:'Vector3f') -> float:
        return self.x * vec.x + self.y * vec.y + self.z * vec.z
    
    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
    
    def normalized(self):
        return self / self.length()

    def tuple(self) -> tuple[float]:
        return (self.x, self.y, self.z)
    
    def __add__(self, other:'Vector3f'):
        return Vector3f(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other:'Vector3f'):
        return Vector3f(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, val:float):
        return Vector3f(self.x * val, self.y * val, self.z * val)

    def __truediv__(self, val:float):
        return Vector3f(self.x / val, self.y / val, self.z / val)
    
    def __str__(self):
        return f"{self.x} {self.y} {self.z}"
    
    def __neg__(self):
        return Vector3f(-self.x, -self.y, -self.z)

    
    def distance(self, other:'Vector3f') -> float:
        return (self - other).length()


class Vector3i:
    x:int
    y:int
    z:int
    def __init__(self, *args) -> None:
        if len(args) < 3:
            self.x = 0
            self.y = 0
            self.z = 0
            return
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]

    def read(self, stream:BytesIO):
        self.z = struct.unpack(">i", stream.read(4))[0]
        self.y = struct.unpack(">i", stream.read(4))[0]
        self.x = struct.unpack(">i", stream.read(4))[0]

    def write(self, stream:BytesIO):
        stream.write(struct.pack(">i", self.x))
        stream.write(struct.pack(">i", self.y))
        stream.write(struct.pack(">i", self.z))

    def __str__(self):
        return f"{self.x} {self.y} {self.z}"

    def inc(self):
        self.x += 1
        self.y += 1
        self.z += 1

    def dec(self):
        self.x -= 1
        self.y -= 1
        self.z -= 1
    
    def readObj(self, line:str):
        header, x, y, z = line.split()
        assert header == "f"
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    def flipNormal(self):
        newX = self.z
        newZ = self.x

        self.x = newX
        self.z = newZ
    
    def tuple(self):
        return (self.x, self.y, self.z)


class Sphere:
    pos:Vector3f
    radius:float

    def __init__(self) -> None:
        self.pos = Vector3f()
        self.radius = 0.0

    def read(self, stream:BytesIO):
        self.pos.read(stream)
        self.radius = struct.unpack(">f", stream.read(4))[0]

    def write(self, stream:BytesIO):
        self.pos.write(stream)
        stream.write(struct.pack(">f", self.radius))

class VertexTable:
    verticies:list[Vector3f]

    def __init__(self) -> None:
        self.verticies = []

    def setList(self, vert:list[Vector3f]):
        self.verticies = vert

    def read(self, stream:BytesIO):
        count:int = struct.unpack(">i", stream.read(4))[0]
        for i in range(count):
            self.verticies.append(Vector3f())
            self.verticies[i].read(stream)

    def write(self, stream:BytesIO):
        stream.write(struct.pack(">i", len(self.verticies)))
        for vertex in self.verticies:
            vertex.write(stream)
    
    def findCenter(self) -> Vector3f:
        sum:Vector3f = Vector3f()
        for vec in self.verticies:
            sum += vec
        return sum / len(self.verticies)

    def findFurthestDistance(self, point:Vector3f) -> float:
        dist:float = 0.0
        for vec in self.verticies:
            newDist = point.distance(vec)
            if newDist > dist:
                dist = newDist
        return dist
    



class Triangle:
    verticies:Vector3i
    trianglePlane:Plane
    edgePlanes:list[Plane, Plane, Plane]

    def __init__(self) -> None:
        self.verticies = Vector3i()
        self.trianglePlane = Plane()
        self.edgePlanes = [Plane(), Plane(), Plane()]

    def read(self, stream:BytesIO):
        self.verticies.read(stream)
        self.trianglePlane.read(stream)
        for plane in self.edgePlanes:
            plane.read(stream)
    
    def write(self, stream:BytesIO):
        self.verticies.write(stream)
        self.trianglePlane.write(stream)
        for plane in self.edgePlanes:
            plane.write(stream)
    
    def toFace(self):
        return self.verticies.tuple()


class TriangleTable:
    triangles:list[Triangle]
    def __init__(self) -> None:
        self.triangles = []
    def read(self, stream:BytesIO):
        count:int = struct.unpack(">i", stream.read(4))[0]
        for i in range(count):
            self.triangles.append(Triangle())
            self.triangles[i].read(stream)
    def write(self, stream:BytesIO):
        stream.write(struct.pack(">i", len(self.triangles)))
        for tri in self.triangles:
            tri.write(stream)

    



class TriIndexList:
    indicies:list[int]
    def __init__(self) -> None:
        self.indicies = []
    def read(self, stream:BytesIO):
        count:int = struct.unpack(">i", stream.read(4))[0]
        for _ in range(count):
            self.indicies.append(struct.unpack(">i", stream.read(4))[0])
    def write(self, stream:BytesIO):
        stream.write(struct.pack(">i", len(self.indicies)))
        for idx in self.indicies:
            stream.write(struct.pack(">i", idx))




class OBB:
    planes:list[Plane] # 6
    center:Vector3f
    vecs:list[Vector3f] # 3
    minimums:list[float] # 3
    maximums:list[float] # 3
    a:None # OBB
    b:None # OBB
    mainPlane:Plane
    triIndexList:TriIndexList
    sphere:Sphere

    def __init__(self) -> None:
        self.planes   = [Plane(), Plane(), Plane(), Plane(), Plane(), Plane()]
        self.center   = Vector3f()
        self.vecs     = [Vector3f(), Vector3f(), Vector3f()]
        self.minimums = [0.0, 0.0, 0.0]
        self.maximums = [0.0, 0.0, 0.0]
        self.mainPlane = Plane()
        self.triIndexList = None
        self.sphere = Sphere()
        self.OBBa = None
        self.OBBb = None
    
    def read(self, stream:BytesIO):
        for plane in self.planes:
            plane.read(stream)
        self.center.read(stream)
        for vec in self.vecs:
            vec.read(stream)
        for i in range(3):
            self.minimums[i] = struct.unpack(">f", stream.read(4))[0]
            self.maximums[i] = struct.unpack(">f", stream.read(4))[0]
        self.mainPlane.read(stream)
        print(self.mainPlane)
        self.sphere.read(stream)
        tri = int(stream.read(1).hex(), 16)
        print("tri idx", tri)
        if tri == 1:
            self.triIndexList = TriIndexList()
            self.triIndexList.read(stream)
        nesting:int = int(stream.read(1).hex(), 16)
        print(nesting)
        if nesting & 1:
            self.OBBa = OBB()
            self.OBBa.read(stream)
        if nesting & 2:
            self.OBBb = OBB()
            self.OBBb.read(stream)

    def write(self, stream:BytesIO):
        for plane in self.planes:
            plane.write(stream)
        self.center.write(stream)
        for vec in self.vecs:
            vec.write(stream)
        for i in range(3):
            stream.write(struct.pack(">f", self.minimums[i]))
            stream.write(struct.pack(">f", self.maximums[i]))
        self.mainPlane.write(stream)
        self.sphere.write(stream)
        if self.triIndexList:
            print(f"wrote: {stream.write(bytes([1]))}")
            self.triIndexList.write(stream)
        else:
            stream.write(bytes([0]))
        nesting:int = 3
        if not self.OBBa:
            nesting &= 2
        if not self.OBBb:
            nesting &= 1
        stream.write(bytes([nesting]))
        if self.OBBa:
            self.OBBa.write(stream)
        if self.OBBb:
            self.OBBb.write(stream)

        


class OBBTree:
    VtxTable: VertexTable
    TriTable: TriangleTable
    obb:      OBB
    def __init__(self) -> None:
        self.VtxTable = VertexTable()
        self.TriTable = TriangleTable()
        self.obb = OBB()

    def read(self, stream:BytesIO):
        self.VtxTable.read(stream)
        self.TriTable.read(stream)
        self.obb.read(stream)

    def write(self, stream:BytesIO):
        self.VtxTable.write(stream)
        self.TriTable.write(stream)
        self.obb.write(stream)

    def makeOBB(self):
        self.obb.center = self.GetCenter()
        self.obb.minimums, self.obb.maximums = self.GetMinMax()
        self.obb.vecs = [Vector3f(*vec) for vec in [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]]
        self.obb.sphere = self.GetSphere()
        self.obb.planes = self.GetPlanes()
        self.obb.mainPlane = Plane(0.0, 1.0, 0.0, 0.0)
        self.obb.triIndexList = TriIndexList()
        # lazy way to generate a working triIndexList
        self.obb.triIndexList.indicies = list(range(len(self.TriTable.triangles)))
        
    
    def makePlanes(self, points:list[Vector3f]) -> list[Plane]:
        planeKey =\
           ((0, 4, 5),
            (1, 2, 3),
            (0, 3, 5),
            (2, 6, 7),
            (4, 5, 6),
            (2, 4, 7))
        return [triToPlane((points[a], points[b], points[c])) for a, b, c in planeKey]
    
    def GetCenter(self):
        centers = Vector3f()
        for tri in self.TriTable.triangles:
            face = tri.toFace()
            a = self.VtxTable.verticies[face[0]]
            b = self.VtxTable.verticies[face[1]]
            c = self.VtxTable.verticies[face[2]]

            centers += (a + b + c) / 3
        return centers / len(self.TriTable.triangles)
    
    def GetMinMax(self):
        mini = [+1e10, +1e10, +1e10]
        maxi = [-1e10, -1e10, -1e10]
        baseMtx = [[1.0, 0.0, 0.0],
                   [0.0, 1.0, 0.0],
                   [0.0, 0.0, 1.0]]
        for i, mainVec in enumerate(baseMtx):
            mainVec = Vector3f(*mainVec)
            for tri in self.TriTable.triangles:
                face = tri.toFace()
                a = self.VtxTable.verticies[face[0]]
                b = self.VtxTable.verticies[face[1]]
                c = self.VtxTable.verticies[face[2]]
                
                for vec in (a, b, c):
                    val = (vec - self.obb.center).dot(mainVec)
                    if val < mini[i]:
                        mini[i] = val
                    if val > maxi[i]:
                        maxi[i] = val
        return (mini, maxi)
    
    def GetSphere(self):
        VecX = Vector3f(*[vec.x for vec in self.obb.vecs])
        VecY = Vector3f(*[vec.y for vec in self.obb.vecs])
        VecZ = Vector3f(*[vec.z for vec in self.obb.vecs])

        MaxiX = Vector3f(*self.obb.maximums).dot(VecX)
        MaxiY = Vector3f(*self.obb.maximums).dot(VecY)
        MaxiZ = Vector3f(*self.obb.maximums).dot(VecZ)

        MiniX = Vector3f(*self.obb.minimums).dot(VecX)
        MiniY = Vector3f(*self.obb.minimums).dot(VecY)
        MiniZ = Vector3f(*self.obb.minimums).dot(VecZ)

        MaxiVec = Vector3f(MaxiX, MaxiY, MaxiZ) + self.obb.center
        MiniVec = Vector3f(MiniX, MiniY, MiniZ) + self.obb.center
        
        sphere = Sphere()
        sphere.pos = (MaxiVec + MiniVec) / 2

        MaxiDiff = MaxiVec - self.obb.center
        MiniDiff = MiniVec - self.obb.center

        lenMaxi = MaxiDiff.length()
        lenMini = MiniDiff.length()

        sphere.radius = lenMaxi if lenMaxi > lenMini else lenMini

        return sphere
    
    def GetPlanes(self):
        planes = []

        VecX = self.obb.vecs[0]
        VecY = self.obb.vecs[1]
        VecZ = self.obb.vecs[2]

        center = self.obb.center
        maxi = Vector3f(*self.obb.maximums)
        mini = Vector3f(*self.obb.minimums)

        plane = Plane()
        plane.setVec(VecX)
        plane.d = plane.getVec().dot(center + VecX * maxi.x)
        planes.append(plane)

        plane = Plane()
        plane.setVec(VecY)
        plane.d = plane.getVec().dot(center + VecY * maxi.y)
        planes.append(plane)

        plane = Plane()
        plane.setVec(VecZ)
        plane.d = plane.getVec().dot(center + VecZ * maxi.z)
        planes.append(plane)

        plane = Plane()
        plane.setVec(-VecX)
        plane.d = plane.getVec().dot(center + VecX * mini.x)
        planes.append(plane)

        plane = Plane()
        plane.setVec(-VecY)
        plane.d = plane.getVec().dot(center + VecY * mini.y)
        planes.append(plane)

        plane = Plane()
        plane.setVec(-VecZ)
        plane.d = plane.getVec().dot(center + VecZ * mini.z)
        planes.append(plane)

        return planes


        

def triToPlane(points:list[Vector3f, Vector3f, Vector3f]) -> Plane:
    a = points[0]
    b = points[1]
    c = points[2]

    ab = a - b
    cb = b - c

    n = ab.cross_product(cb)
    n = n.normalized()

    d = abs(n.dot(a))

    return Plane(n.x, n.y, n.z, d)
        


class ObjFile:
    verticies:list[Vector3f]
    faces:list[Vector3i]
    def __init__(self) -> None:
        self.verticies = []
        self.faces = []

    def read_vertex(self, v_data):
        split = v_data.split("/")
        v = int(split[0])
        return v

    # stolen from Yoshi2
    def readObj(self, objfile:list[str], flip_yz:bool=False):
                
        for i, line in enumerate(objfile):
            line = line.strip()
            args = line.split(" ")
            
            if len(args) == 0 or line.startswith("#"):
                continue
            cmd = args[0]
                
            if cmd == "v":
                if "" in args:
                    args.remove("")
                vec = Vector3f(*map(float, args[1:4]))
                if flip_yz:
                    vec.flipYZ()
                self.verticies.append(vec)
            elif cmd == "f":
                # if it uses more than 3 vertices to describe a face then we panic!
                if len(args) != 4:
                    raise RuntimeError("Model needs to be triangulated! Only faces with 3 vertices are supported.")
                face = Vector3i(*map(self.read_vertex, args[1:4]))
                face.dec()
                face.flipNormal()
                print(face)
                self.faces.append(face)

    def makeVertexTable(self) -> VertexTable:
        table = VertexTable()
        table.setList(self.verticies)
        return table
    

    def makeTriTable(self) -> TriangleTable:
        table:TriangleTable = TriangleTable()
        for vertIdxs in self.faces:
            a:Vector3f = self.verticies[vertIdxs.x]
            b:Vector3f = self.verticies[vertIdxs.y]
            c:Vector3f = self.verticies[vertIdxs.z]

            ab = a - b
            bc = b - c
            ca = c - a
            ac = a - c

            cross_norm = -ab.cross_product(ac)
            if cross_norm.x == cross_norm.y == cross_norm.z:
                tan1 = tan2 = tan3 = norm = Vector3f(0.0, 0.0, 0.0)
            else:
                norm = cross_norm.normalized()
                tan1 = ab.cross_product(norm).normalized()
                tan2 = bc.cross_product(norm).normalized()
                tan3 = ca.cross_product(norm).normalized()
                
                mid = (a + b + c) / 3.0

            tri = Triangle()

            tri.trianglePlane.setVec(norm)
            tri.trianglePlane.d = norm.dot(mid)

            tri.edgePlanes[0].setVec(tan1)
            tri.edgePlanes[0].d = a.dot(tan1)

            tri.edgePlanes[1].setVec(tan2)
            tri.edgePlanes[1].d = b.dot(tan2)

            tri.edgePlanes[2].setVec(tan3)
            tri.edgePlanes[2].d = c.dot(tan3)

            tri.verticies = vertIdxs

            table.triangles.append(tri)
        return table
    
    def toOBBTree(self) -> OBBTree:
        tree:OBBTree = OBBTree()
        tree.VtxTable = self.makeVertexTable()
        tree.TriTable = self.makeTriTable()
        tree.makeOBB()
                
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input",
                        help=(  "Filepath of the wavefront .obj file that will be converted into collision. "))
    parser.add_argument("--pla2obj", action="store_true",
                        help="Use this option to create an OBJ file out of a .pla file")
    parser.add_argument("output", default=None, nargs = '?',
                        help="Output path of the created collision file. If --pla2obj is set, output path of the created obj file")
    args = parser.parse_args()
    base_dir = os.path.dirname(args.input)
    if args.pla2obj:
        with open(args.input, "rb") as f:
            data:BytesIO = BytesIO(f.read())
        thing = OBBTree()
        thing.read(data)

        out = args.output if args.output else os.path.join(base_dir, "platform.obj")
        with open(out, "w") as f:
                f.write("# VERTICES BELOW\n\n") 
                for vector in thing.VtxTable.verticies:
                    f.write(f"v {vector.x} {vector.y} {vector.z}\n")
                    
                f.write("\n# FACES BELOW\n\n")
                i = 0
                
                for triangle in thing.TriTable.triangles:
                    
                    vecI:Vector3i = Vector3i(*triangle.toFace())
                    vecI.inc()
                    f.write(f"f {vecI.x} {vecI.y} {vecI.z}\n")
                    i += 1
    else:
        with open(args.input, "r") as f:
            data:list[str] = f.readlines()
        inObj:ObjFile = ObjFile()
        inObj.readObj(data)
        outOBB:OBBTree = OBBTree()
        outOBB.VtxTable = inObj.makeVertexTable()
        outOBB.TriTable = inObj.makeTriTable()
        outOBB.makeOBB()
        out = args.output if args.output else os.path.join(base_dir, "platform.pla")
        with open(out, "wb") as f:
            data:BytesIO = BytesIO()
            outOBB.write(data)
            f.write(data.getbuffer())


# Used for make json struct reports
def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey)) 
            for key, value in obj.__dict__.items() 
            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj

if __name__ == "__main__":
    main()

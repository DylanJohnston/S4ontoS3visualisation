import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from collections import defaultdict


def symmetry_matrix(cycle:int):
    '''
    This function returns matrix representation of 'cycle' of S4 acting on tetrahedron with vertices
    [-1, -1, 1],[1, 1, 1],[-1, 1, -1],[1, -1, -1].

    This is done by realising vertices 1,2,3 form a basis of R^3. So we write the cycle as a permutation matrix w.r.t
    this basis, then change the basis to the standard one.

    Attributes:
        cycle: int
            An integer representating an element of S4 in one line notation.
            e.g. the element of S4 given by 1 -> 3, 3-> 4, 4 -> 1 should be passed as (3241).
    '''
    CoB_matrix = np.column_stack([[-1, -1, 1],[1, 1, 1],[-1, 1, -1]])
    CoB_inv = np.linalg.inv(CoB_matrix)
    vertex4_in_vertex_basis = CoB_inv @ np.array([1, -1, -1])
    cycle_str = str(cycle)

    perm_matrix_wrt_vertex_basis = np.zeros((3, 3))
    for i in range(3):
        #place '1' in each column of perm_matrix, depending on where basis elements go
        #note: columns of perm indexing starts from 0.
        if int(cycle_str[i]) == 4:
            #(i+1) is sent to vertex 4 by the cycle. Set ith column equal to vertex 4 wrt bases (vert1,vert2,vert3)
            perm_matrix_wrt_vertex_basis[:,i] = vertex4_in_vertex_basis
        else:
            perm_matrix_wrt_vertex_basis[int(cycle_str[i])-1][i] = 1

    return CoB_matrix @ perm_matrix_wrt_vertex_basis @ CoB_inv


def edge_hidden(camera_loc, vertices, edges):
    """
    A function which determines whether each edge of our shape with vertices 'vertices' is fully visible when looked at
    using a camera/POV with position 'camera_loc'.

    Arguments:
    camera_loc: a 3-tuple representing the point in space of the camera (facing towards the origin).
    vertices: a lit of vertices of our shape, ideally a 2d numpy array.
    edges: a list of tuples (i,j) denoting edge from vertices[i] to vertices[j]

    Returns dict:
        Dictionary with (key:value) pairs given by an edge in 'edges', and whether the edge is visible when looked at
        from position 'camera_loc'.
    """

    #each of the four faces describes a plane. We describe each plane using a normal vector and 'd' value where Plane is {x: x \dot n = d}.
    edge_behind = defaultdict(bool) #an edge is NOT behind by default, we need to prove it is behind.
    for i in range(4):
        face_vertices = np.array([v for ind,v in enumerate(vertices) if ind != i]) #list of three vertices, defining a face.
        normal_vector = np.cross((face_vertices[1]-face_vertices[0]),(face_vertices[2]-face_vertices[0]))
        d_value = np.dot(normal_vector,face_vertices[0])

        #The face is defined using three edges, thus, there are three edges which do not define it. These will be called "opposite edges"
        #and consist of edges with start/end point being the vertex left out of face_vertices above (i.e. the 'opposite vertex').

        opposite_edges = [e for e in edges if i in e]

        #For the opposite vertex, if the line segment from 'camera_loc' to this vertex passes through the opposite face. Then all opposite edges
        #are hidden (since they start or end at a hidden vertex).
        #To check this, we take the line 'camera_loc + t(vertex - camera_loc)' and find the intersection of this line
        #and the plane containing the opposite face to the vertex (i.e. find the t value). The following fucntion finds this t value.:

        def find_intersection(start_pt, end_pt, plane_normal, d_val):
            """
            Given a line defined by 'start_pt + t(end_pt-start_pt), and a normal vector and d_value defining a plane. Finds 't' such that
            the line and plane intersect.

            start_pt: 3d vector (probably numpy array)
            end_pt: 3d vector (probably numpy array)
            plane_normal: 3d vector (probably numpy array)
            d_value: numeric (int,float etc)

            Returns:
                t value (int), and the intersection vector (numpy array len 3)
            """
            t_num = d_val - np.dot(plane_normal, start_pt)
            t_denom = np.dot(plane_normal, end_pt - start_pt)
            if t_denom == 0:
                return None
            t = t_num/t_denom
            return t, start_pt + t*(end_pt-start_pt)

        try:
            t = find_intersection(camera_loc, vertices[i], normal_vector, d_value)[0]
        except TypeError:
            #intersection returned None because line 'camera_loc -> vertices[i]' is parallel to normal. So "t=inf".
            # For us, t = LARGE (actually, larger than 1... see next if statment) will do.
            t = 2

        #if t<1 then the line meets the plane before it meets the vertex, i.e. the vertex is "behind the plane".
        # Otherwise, the vertex is in front of the plane. Therefore, edges will be preliminarily set to NOT behind.
        if t >=1:
            continue #move to the next vertex

        #if we get to this point, then t < 1, so the line from camera_loc to vertex meets the plane before it reaches the vertex.
        #We now check if each edge protruding from this vertex is behind the shape. To do this, we take a sample of points on each edge,
        #and check if the intersection point of the line from 'camera_loc to this point on the edge intersects the hull of our face_vertices.
        #If any point on the edge returns True to this, then the edge is behind and we move on.

        #The following is a function to check if a point lies in a convex hull of points. Ref:
        #https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if
        #-a-point-lies-in-the-convex-hull-of-a-point-cl/43564754#43564754
        def in_hull(points, x):
            from scipy.optimize import linprog
            n_points = len(points)
            n_dim = len(x)
            c = np.zeros(n_points)
            A = np.r_[points.T, np.ones((1, n_points))]

            b = np.r_[x, np.ones(1)]
            lp = linprog(c, A_eq=A, b_eq=b)
            return lp.success

        for edge in opposite_edges:
            for d in np.linspace(0.1, 0.9, num=5):
                edge_point = vertices[edge[0]] +d*(vertices[edge[1]]-vertices[edge[0]])
                try:
                    intersection = find_intersection(camera_loc, edge_point, normal_vector, d_value)[1]
                except TypeError:
                    continue
                edge_pt_behind_shape = in_hull(face_vertices, intersection)
                if edge_pt_behind_shape:
                    #point on edge is hidden behind shape.
                    edge_behind[edge] = True
                    break #no need to check other points along this edge
    return  edge_behind

def axes_3d_camera_position(elev, azim, r=9):
    """
    A 3d plot in matplotlib forces us to look at our 3d shape from a particular angle.
    This is controlled by elevation ('elev') and azimuth ('azim'), with distance from origin unknown.
    This function takes 'elev' and 'azim' and a distance from the origin 'r' and finds the (x,y,z) coordinates.

    Parameters:
    elev : Elevation angle in degrees.
    azim : Angle in degrees rotating about z-axis, with angle = 0 corresponding to the positive x-axis. Positive = anticlockwise.
    r    : Distance from the origin.

    Returns:
    A tuple (x, y, z) representing the camera's position in 3D space.
    """

    elev_rad = np.deg2rad(elev)
    azim_rad = np.deg2rad(azim)

    # Calculate cartesian coords, see https://en.wikipedia.org/wiki/Spherical_coordinate_system#Cartesian_coordinates
    x = r * np.cos(elev_rad) * np.cos(azim_rad)
    y = r * np.cos(elev_rad) * np.sin(azim_rad)
    z = r * np.sin(elev_rad) * 4/3 #trial and error shows the z-coordinate is 4/3 times what one would expect from spherical coordinates... I don't know why...

    return np.array([x, y, z])


def plot_3d_shape(ax, vertices, edges):
    '''
    This function clears the axes 'ax' and plots the 3d shape with vertices `vertices' and edges 'edges'.
    This will be used alongside matplotlib.animation.FuncAnimation to create a gif of a symmetry of a 3d shape.

    ax: a matplotlib.Axes3D object
    vertices: a list of 3-tuples, representing vertices of the shape
    edges: a list of 2-tuples (i,j) denoting edge from vertices[i] to vertices[j]
    '''
    ax.clear()
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1,1])
    ax.grid(False)
    ax.set_axis_off()
    ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], color='black', s=40)

    #A boolean array with entry in index 'i' stating whether vertices[i] is hidden w.r.t camera location.
    edges_hidden = edge_hidden(camera_loc=camera_location, vertices=vertices, edges=edges)

    for edge in edges:
        if edge in [(0,1),(2,3)]:
            edge_color = 'green'
        elif edge in [(0,3), (1,2)]:
            edge_color = 'red'
        else:
            edge_color = 'blue'
        point1 = vertices[edge[0]]
        point2 = vertices[edge[1]]
        if edges_hidden[edge]:
            ax.plot([point1[0], point2[0]], [point1[1], point2[1]], [point1[2], point2[2]], '--', color=edge_color, linewidth=1)
        else:
            ax.plot([point1[0], point2[0]], [point1[1], point2[1]], [point1[2], point2[2]], '-', color = edge_color, linewidth=2)

    for i, vertex in enumerate(vertices):
        #Our view of the 3d plot is from position somewhat like (N,-N,N) for large N
        #So, for points in x>0, y<0 quadrant we shift the label of  the vertex down to see it better.
        #Otherwise we shift the label up.
        if (vertex[0] > 0) & (vertex[1] < 0):
            ax.text(vertex[0], vertex[1], vertex[2]-0.1, f'{i+1}', fontsize=18, va='top')
        else:
            ax.text(vertex[0], vertex[1], vertex[2]+0.1, f'{i+1}', fontsize=18, va='bottom')


def update(frame, ax, transformation_matrix, vertices, edges):
    '''
    frame: int
    ax: matplotlib.Axes object
    transformation_matrix:  2d numpy array reprepresenting a tranfomration on R^3 (in practice, a symmetry of tetrahedron).
    vertices: vertices of the shape
    edges: a list of 2-tuples (i,j) denoting edge from vertices[i] to vertices[j]

    Takes integer 'frame' (in practice between 0 and num_frames, a variable defined globally).

    As frame varies from 0 to num_frames this defines a path from Identity matrix to the passed
    matrix 'transformation_matrix'.

    This function computes the action of each matrix along this path (the precise matrix depending on which
    value 'frame' was passed) on some set of vertices, before plotting the result using 'plot_3d_shape'
    '''
    alpha = frame / num_frames
    intermediate_matrix = (1 - alpha) * np.eye(3) + alpha * transformation_matrix
    transformed_vertices = np.dot(vertices, intermediate_matrix.T)
    plot_3d_shape(ax, transformed_vertices, edges)


if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection='3d')
    ax.view_init(elev=30, azim=-60, roll=0)
    #This camera location is approximate, but as an estimate this is sufficient
    camera_location = axes_3d_camera_position(ax.elev, ax.azim, 1000)
    # Define vertices of a tetrahedron
    # see https://en.wikipedia.org/wiki/Tetrahedron#Cartesian_coordinates
    vertices = np.array([[-1, -1, 1],[1, 1, 1],[-1, 1, -1],[1, -1, -1]])
    # Define the edges between vertices indexed 0,1,2,3 as above
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    num_frames = 150
    frames = np.append(np.arange(num_frames+1),np.full(num_frames//2, num_frames)) #duplicate frames simulate a repeat_delay in the saved gif.

    #generate all elements of S4 in two-line notation.
    from itertools import permutations
    perm = permutations('1234')
    perm_list = [int(''.join(p)) for p in perm]

    def show_animation_for_element(s4twoline):
        ani = FuncAnimation(fig, update, frames=frames, fargs=(ax, symmetry_matrix(s4twoline), vertices, edges),
                            interval=1, repeat=True)
        plt.show()

    def create_all_anims_and_save():
        for s4twoline in perm_list:
            ani = FuncAnimation(fig, update, frames=frames, fargs=(ax,symmetry_matrix(s4twoline),vertices, edges),
                                interval = 1, repeat=True)
            ani.save(f'GIFs/tetrahedron_reflection_swap_{s4twoline}.gif', writer="pillow", fps=50)
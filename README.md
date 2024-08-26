# S4 onto S3 Visualization

A web app I created to aid in visualizing the surjective map from $S_4$ onto $S_3$. It can be found here:

<a href="https://dylanjohnston.github.io/S4ontoS3visualisation/" target="_blank">https://dylanjohnston.github.io/S4ontoS3visualisation</a>

The repository is made up of three main parts:

### `./GIFs` directory

This directory contains 24 `.gif` files, each of which is an animation showing the action of an element of $S_4$ on the vertices of a regular tetrahedron.

### `animations.py`

This Python file contains the code used to produce the 24 animations. It works by defining a $3$D linear transformation $T$ representing the action of each element of $S_4$. Then, a path from the identity to $T$ is defined via $(1-a)\text{Id} + aT$. Each "frame" corresponds to a value of $a \in [0,1]$. The animation is created by finding the image of the tetrahedron under an evenly spaced sample of points along this path and stitching them together using `matplotlib.animation`.

Another fun problem was determining whether edges should be drawn using solid or dotted lines. This was accomplished using linear algebra and concepts involving convex hulls. Roughly, each face of the tetrahedron defines a plane, and each point along an edge defines a line passing through the camera's position and the point. The intersection of this line and the plane was found, and it was then checked if the intersection point lay on the face. This was done using some theory involving convex hulls and linear programming. If a sample point along a given edge produced an intersection point lying within the convex hull, the edge was considered hidden and was drawn using a dotted line.

### The web files (HTML, CSS, JS, PNG)

My first experience with frontend development. :)

The JS is used to dynamically update the $S_4$ elements throughout the webpage based on the notation type selected. Further, once an element of $S_4$ is selected, the JS script updates the animation being displayed, the image of the element under the map, and the explicit descriptions of the elements (i.e., describing where the elements send each member of the acted-on set).


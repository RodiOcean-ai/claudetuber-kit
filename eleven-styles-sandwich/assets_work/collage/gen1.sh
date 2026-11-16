MP="py -3.13 <your-picture-maker>/make-picture.py"
VIN="Vintage 1960s magazine advertisement print photograph, slightly faded warm colours, visible print grain and fine halftone dots, old printed paper look,"
ISO="isolated on a solid flat pure green background, no shadow, nothing else in frame, no text."
O=assets_work/collage
$MP "Flat lay photograph of a sheet of brown kraft paper filling the whole frame edge to edge, slightly crumpled with soft creases, even soft light, natural paper fibres, no objects, no text, no shadow edges." $O/kraft --size 1664x928 --n 3 --seed 3101
$MP "A long torn strip of plain white paper lying flat, ragged torn fibrous edges on both long sides, slightly uneven, $ISO" $O/paper --size 1664x928 --n 3 --seed 3201
$MP "One short piece of beige paper masking tape lying flat, both ends torn with jagged edges, slightly translucent crepe paper texture, $ISO" $O/tape --size 1328x1328 --n 4 --seed 3301
$MP "$VIN one slice of white sandwich bread with a golden-brown crust, classic slice shape with a domed top, lying flat, seen from slightly above, $ISO" $O/vbread --size 1328x1328 --n 3 --seed 3401
$MP "$VIN an open plain glass jar of creamy tan-brown peanut butter with no label, seen from slightly above, $ISO" $O/vjar --size 1328x1328 --n 3 --seed 3501
$MP "$VIN one silver butter knife with a rounded blade lying flat diagonally, $ISO" $O/vknife --size 1328x1328 --n 3 --seed 3601
$MP "$VIN a woman's hand and wrist holding a silver butter knife as if about to spread, only the hand and wrist, no face, no person, $ISO" $O/vhand --size 1328x1328 --n 3 --seed 3701
$MP "$VIN a white bread peanut butter sandwich cut diagonally into two triangle halves, slightly apart, filling visible, seen from slightly above, $ISO" $O/vhalves --size 1328x1328 --n 3 --seed 3801
$MP "$VIN an empty round vintage china plate with a thin pastel turquoise rim pattern, seen from slightly above, $ISO" $O/vplate --size 1328x1328 --n 3 --seed 3901

const WIDTH_BREAKPOINT = 1955  // less will remove one column
const SINGLE_COL_WIDTH_BREAKPOINT = 1555
const X_OFFSET = 55 // leftside offset whitespace in the PNGs
const Y_OFFSET = 5  // make room for arrows pointing at the cytoban
const OFFSET_X = 60;
const OFFSET_Y = 30;
const CHROMOSOMES = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                     '11', '12', '13', '14', '15', '16', '17', '18',
                     '19', '20', '21', '22', 'X', 'Y'];

// Ideogram measurements used for cropping to a nice picture
const CHROMSPECS_LIST =
      [{name: '1', length: 500, cent_start: 255, cent_length: 13 },
       {name: '2', length: 487, cent_start: 193, cent_length: 13 },
       {name: '3', length: 397, cent_start: 187, cent_length: 13 },
       {name: '4', length: 385, cent_start: 105, cent_length: 13 },
       {name: '5', length: 367, cent_start: 102, cent_length: 10 },
       {name: '6', length: 346, cent_start: 125, cent_length: 13 },
       {name: '7', length: 321, cent_start: 125, cent_length: 10 },
       {name: '8', length: 293, cent_start: 98, cent_length: 8 }, //
       {name: '9', length: 283, cent_start: 107, cent_length: 8 },
       {name: '10', length: 271, cent_start: 88, cent_length: 8 },
       {name: '11', length: 270, cent_start: 111, cent_length: 10 },
       {name: '12', length: 268, cent_start: 78, cent_length: 10 },
       {name: '13', length: 232, cent_start: 44, cent_length: 8 },
       {name: '14', length: 217, cent_start: 42, cent_length: 8 },
       {name: '15', length: 207, cent_start: 40, cent_length: 8 },
       {name: '16', length: 182, cent_start: 80, cent_length: 8 },
       {name: '17', length: 165, cent_start: 55, cent_length: 8 },
       {name: '18', length: 158, cent_start: 42, cent_length: 8 },
       {name: '19', length: 119, cent_start: 60, cent_length: 8 },
       {name: '20', length: 127, cent_start: 60, cent_length: 8 },
       {name: '21', length: 95, cent_start: 33, cent_length: 8 },
       {name: '22', length: 104, cent_start: 38, cent_length: 8 },
       {name: 'X', length: 312, cent_start: 127, cent_length: 8 },
       {name: 'Y', length: 107, cent_start: 32, cent_length: 4 }]


/**
 * Iterate case.individuals. If a path to a image directory
 * is set, get panels on the page and add image content
 */
function add_image_to_individual_panel(individuals, institute, case_name){
    for (var i=0; i<individuals.length; i++){
        if(individuals[i].chromograph_images){
            draw_tracks(individuals[i], institute, case_name)
        }
    }
}


/**
 * Draw RHO call pictures -coverage- and UPD pictures -color coded
 * genome regions- onto the dashboard.
 */
function draw_tracks(individual, institute, case_name){
    // First add all new image elements to a fragment, then lastly add the fragmen to main DOM.
    var fragment = document.createDocumentFragment();
    const CYT_HEIGHT = 50 ;
    const CYT_WIDTH = 530 ;
    var number_of_columns = $(window).width() < WIDTH_BREAKPOINT? 2:3
		if( $(window).width() < SINGLE_COL_WIDTH_BREAKPOINT){
				number_of_columns = 1
		}
    var svg_element = document.getElementById("svg_" + individual["individual_id"])
    clear_svg(svg_element)
    svg_element = document.getElementById("svg_" + individual["individual_id"]) // get svg_element again, now clean
    set_svg_size(svg_element, number_of_columns)


    if (individual.chromograph_images.autozygous != undefined){
        var autozygous_imgPath = create_path(institute, case_name, individual, 'autozygous_images')
        var autozygous_images = make_names("autozygous-");
    }
    if (individual.chromograph_images.upd_regions != undefined){
        var upd_regions_imgPath = create_path(institute, case_name, individual, 'upd_regions_images')
        var upd_regions_images = make_names("upd_regions-");
    }
    if (individual.chromograph_images.coverage != undefined){
        var coverage_imgPath = create_path(institute, case_name, individual, 'coverage_images')
        var coverage_images = make_names("coverage-");
    }

    // ideograms always exist
    var ideo_imgPath = static_path_ideograms(institute, case_name, individual, 'ideaograms')
    var ideo_images = make_names('')
    var autozygous_imgObj = new Image()
    var upd_regions_imgObj = new Image()
    var coverage_imgObj = new Image()
    var chromspecs_list = get_chromosomes(individual.sex)
    const chromspecs_list_length = chromspecs_list.length

    for(i = 0; i< chromspecs_list_length; i++){
        x_pos = i % number_of_columns == 0? 0 : CYT_WIDTH * (i% number_of_columns) + OFFSET_X + 5
        y_pos =  Math.floor( i/number_of_columns ) * 140;
        var graphics_fragment = document.createDocumentFragment();
        var g = document.createElementNS('http://www.w3.org/2000/svg','g');
        var ideo_image = make_svgimage(ideo_imgPath + ideo_images[i],
                                       x_pos+15,
                                       y_pos,
                                       "25px", "500px", );

        var t = chromosome_text(CHROMOSOMES[i], x_pos, y_pos);
        var clipPath = make_clipPath(CHROMSPECS_LIST[i], x_pos, y_pos)
        path_ideo = make_ideogram_shape(CHROMSPECS_LIST[i], x_pos, y_pos)

        ideo_image.setAttributeNS(null, 'clip-path', "url(#clip-chr"+CHROMSPECS_LIST[i].name +")")
        graphics_fragment.appendChild(ideo_image);

        // add polygon to outline ideogram
        var border_path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        border_path.setAttributeNS(null, 'd', path_ideo)
        border_path.setAttributeNS(null, 'style', "stroke:black;stroke-width:1")
        border_path.setAttributeNS(null, 'fill-opacity', '0.0')

        graphics_fragment.appendChild(clipPath);
        graphics_fragment.appendChild(t);
        graphics_fragment.appendChild(border_path)

	if(individual.chromograph_images.upd_regions){
            var upd_img = ideo_image.cloneNode()
            upd_img = update_svgimage(upd_img, upd_regions_imgPath + upd_regions_images[i],
                                      x_pos+15,
                                      y_pos + 90,
                                      "25px", "500px", );
            graphics_fragment.appendChild(upd_img);
        }

        if(individual.chromograph_images.autozygous){
            var auto_img = ideo_image.cloneNode()
            auto_img = update_svgimage(auto_img, autozygous_imgPath + autozygous_images[i],
                                       x_pos + 0+15,  //
                                       y_pos + 30 , // place below UPD
                                       "25px", "500px", );
            graphics_fragment.appendChild(auto_img);
        }

        if(individual.chromograph_images.coverage){
            var cov_img = ideo_image.cloneNode()
            cov_img = update_svgimage(cov_img, coverage_imgPath + coverage_images[i],
                                      x_pos + 0+15, //
                                      y_pos + 60 , // place below UPD
                                      "25px", "500px", );
            graphics_fragment.appendChild(cov_img);
        }

        g.appendChild(graphics_fragment)
        fragment.append(g)
    }
    svg_element.append(fragment)
}


/**
 * Clear svg palette before painting new graphics, otherwise they
 * will stack ontop of eachother
 */
function clear_svg(svg_element){
    var parent  = svg_element.parentElement
    var emptySvg = svg_element.cloneNode(false)
    parent.removeChild(svg_element)
    parent.appendChild(emptySvg)
}


/**
 * Set svg size depending number of columns
 *
 */
function set_svg_size(svg_element, number_of_columns){
		switch(number_of_columns){
			case 1:
				svg_element.setAttribute('width', 600)
				svg_element.setAttribute('height', 3350)
				break;
			case 2:
				svg_element.setAttribute('width', 1200)
				svg_element.setAttribute('height', 1700)
				break;
			case 3:
				svg_element.setAttribute('width', 1550)
				svg_element.setAttribute('height', 1100)
				break;
    }
}


/**
 * Create an URL path
 *
 */
function create_path(institute, case_name, individual, dir_name){
    // XXX: institute is not in use, institute is magically(?) added to the url in a request
    return case_name + "/" + individual["individual_id"] + "/" + dir_name + "/"
}

/**
 * Create an URL path. Ideaograms are static on format:
 *
 *     http://localhost:5000/public/static/ideograms/chromosome-1.png
 *
 */
// TODO: accesses not as above, couldn't figure out how to get the correct URL for Flask
function static_path_ideograms(institute, case_name, individual, dir_name){
    return "/public/static/ideograms/chromosome-"
}


/**
 * Returns an array or filenames based on `prefix` argument
 *
 */
function make_names(prefix){
    var names = [];
    const chrom_length = CHROMOSOMES.length
    for (var i = 0; i < chrom_length; i++){
        id = CHROMOSOMES[i];
        names[i] = prefix+id+".png";
    }
    return names;
}


/**
 * Replace escape charater. Used to make configurations very dynamic.
 *
 */
function replace_escape_char(str, escape_char, substitution){
    return s.replaceAll(str, escape_char, substitution)
}


/**
 * Create and add chromosome id (1-22,x,y) to html dom
 *
 */
function chromosome_text(text, x, y){
    var t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    t.setAttributeNS(null, 'x', x);
    t.setAttributeNS(null, 'y', y+10);
    t.appendChild( document.createTextNode(text) );
    return t;
}


/**
 * Males shall display 24 png:s. Females shall display 23 png:s
 *
 */
function get_chromosomes(sex) {
	if (sex == "2") {
		return CHROMSPECS_LIST.slice(0, CHROMSPECS_LIST.length - 1)
	} else {
		return CHROMSPECS_LIST
	}
}

/**
 * Create a polygon path. Used to give cytoband images -rectangular- rounded
 * ends and a waist at the centromere.
 */
function make_clipPath(chrom, x_offset, y_offset){
    var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    var clipPath = document.createElementNS('http://www.w3.org/2000/svg', 'clipPath');
    clipPath.setAttributeNS(null, 'id', "clip-chr"+chrom.name)
    var p1 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path = make_ideogram_shape(chrom, x_offset, y_offset)
    p1.setAttributeNS(null, 'd', path)

    clipPath.append(p1)
    defs.append(clipPath)
    return clipPath
}


// Return polygon path for ideogram, with optional offset
function make_ideogram_shape(chrom, x_offset, y_offset){
    const c = 10
    x_offset += 0   // make space for text labels
    var centromere = {x: chrom.cent_start + x_offset,
                      y: y_offset,
                      length: chrom.cent_length,}
    var m = "M " + String(chrom.length + x_offset) + " " + String( 25 + y_offset) + " " // path start

    var start_l = {x: chrom.cent_start + chrom.cent_length +5 +5 + x_offset,
                   y: 0 + 25 + y_offset,
                   length: chrom.cent_length }

    var start_u = {x: chrom.cent_start + x_offset,
                   y: y_offset,
                   length: chrom.cent_length}
    var r = 7
    var cent_lower = calc_centromere_lower(start_l)
    var b_left = "L " + " " + String( 30 + x_offset) + " " + String(y_offset + 25) + " "

    // Bezier curve for left bend, format= bezier-1: x,y bezier-2: x,y, endpoint: x,y
    var c1 = "C " + " " + String(15 - r + x_offset) + " " + String(25 + y_offset) + " "
        + String(15 - r + x_offset) + " " + String(y_offset) + " "
        + String(30 + x_offset) + " " + String( y_offset) + " "

    var cent_upper = calc_centromere_upper(start_u)
    var right = "L " + String(chrom.length + x_offset) + " " + String(y_offset) + " "

    // Bezier curve for right bend
    var c2 = "C " + " " + String(chrom.length+15 + r + x_offset) + " " + String(y_offset) + " "
        + String(chrom.length +15 + r + x_offset) + " " + String(y_offset+25) + " "
        + String(chrom.length + x_offset) + " " + String( y_offset+25)+ " "

    path = m + cent_lower + b_left + c1 + cent_upper + right + c2
    return path
}





/**
 * Get centromeres upper waist
 *
 */
function calc_centromere_upper(pos){
    // Upper waist of centromere
    // ------(L1)      (L4)------
    //          \_____/
    //       (L2)      (L3)
    var l1 = "L " + String(pos['x']) + " " + String(pos['y']) + " ";
    var l2 = "L " + String(pos['x']+5) + " " + String(pos['y']+3) + " ";
    var l3 = "L " + String(pos['x']+5+pos.length) + " " + String(pos['y']+3) + " ";
    var l4 = "L " + String(pos['x']+5+pos.length+5) + " " + String(pos['y']) + " ";
    return l1 + l2 + l3 + l4
}


/**
 * Get centromeres lower waist
 *
 */
function calc_centromere_lower(pos){
    // Lower waist of centromere
    //       (L3)-----(L2)
    //        /         \
    // ----(L4)         (L1)-----
    var l1 = "L " + String(pos['x']) + " " + String(pos['y']) + " ";
    var l2 = "L " + String(pos['x']-5) + " " + String(pos['y']-3) + " ";
    var l3 = "L " + String(pos['x']-5-pos.length) + " " + String(pos['y']-3) + " ";
    var l4 = "L " + String(pos['x']-5-pos.length-5) + " " + String(pos['y']) + " ";
    return l1 + l2 + l3 + l4
}


/**
 *
 *
 */
function make_svgimage(src, x, y, height, width){
    var svgimg = document.createElementNS('http://www.w3.org/2000/svg','image');
    svgimg.setAttributeNS('http://www.w3.org/1999/xlink','href', src);
    svgimg.setAttribute('x', String(x));
    svgimg.setAttribute('y', String(y));
    svgimg.setAttribute('height', String(height));
    svgimg.setAttribute('width', String(width));
    return svgimg;
}


function update_svgimage(svgimg, src, x, y, height, width){
    svgimg.setAttributeNS('http://www.w3.org/1999/xlink','href', src);
    svgimg.setAttribute('x', String(x));
    svgimg.setAttribute('y', String(y));
    svgimg.setAttribute('height', String(height));
    svgimg.setAttribute('width', String(width));
    svgimg.setAttribute('clip-path', null);
    return svgimg;
}




/**
 * x_cyt: upper x coordinate of corresponding cytoband
 * y_cyt: upper y coordinate of corresponding cytoband
 *
 *
 *  (a_x, a_y) --------- (b_x, b_y)
 *          \              /
 *           \            /
 *            \          /
 *             (c_x, c_y)
 *
 */
function make_polygon(x_cyt, y_cyt, pos, link, ) {
    const POLY_WIDTH = 10
    var a = document.createElementNS('http://www.w3.org/2000/svg','a');
    a.setAttribute('href', link)
    var poly = document.createElementNS('http://www.w3.org/2000/svg','polygon');
    var ax = String( x_cyt+pos+ X_OFFSET)
    var ay = String( y_cyt -10 )
    var bx = String( x_cyt+pos+POLY_WIDTH +X_OFFSET)
    var by = String( y_cyt -10 )
    var cx = String( x_cyt+pos+ Math.floor(POLY_WIDTH/2) + X_OFFSET )
    var cy = String( y_cyt+Y_OFFSET )

    poly.setAttributeNS(null,'points', ax + ',' + ay + ' ' + bx + ',' + by + ' ' + cx + ',' + cy );
    poly.setAttributeNS(null,'style', "fill:red;stroke:crimson;stroke-width:1");
    a.appendChild(poly)
    return a;
}

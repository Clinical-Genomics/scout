const WIDTH_BREAKPOINT = 1955  // less will remove one column
const X_OFFSET = 55 // leftside offset whitespace in the PNGs
const Y_OFFSET = 5  // make room for arrows pointing at the cytoban
const OFFSET_X = 60;
const OFFSET_Y = 30;
const CHROMOSOMES = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                     '11', '12', '13', '14', '15', '16', '17', '18',
                     '19', '20', '21', '22', 'X', 'Y'];

// Ideogram measurements used for cropping to a nice picture
const CHROMSPECS_LIST =
      [{name: '1', length: 482, cent_start: 245, cent_length: 13 },
       {name: '2', length: 470, cent_start: 185, cent_length: 13 },
       {name: '3', length: 387, cent_start: 180, cent_length: 13 },
       {name: '4', length: 372, cent_start: 105, cent_length: 13 },
       {name: '5', length: 353, cent_start: 105, cent_length: 10 },
       {name: '6', length: 336, cent_start: 121, cent_length: 13 },
       {name: '7', length: 313, cent_start: 125, cent_length: 13 },
       {name: '8', length: 290, cent_start: 100, cent_length: 8 },
       {name: '9', length: 280, cent_start: 103, cent_length: 8 },
       {name: '10', length: 270, cent_start: 90, cent_length: 10 },
       {name: '11', length: 267, cent_start: 115, cent_length: 10 },
       {name: '12', length: 265, cent_start: 80, cent_length: 13 },
       {name: '13', length: 232, cent_start: 47, cent_length: 8 },
       {name: '14', length: 217, cent_start: 47, cent_length: 8 },
       {name: '15', length: 207, cent_start: 47, cent_length: 8 },
       {name: '16', length: 184, cent_start: 82, cent_length: 8 },
       {name: '17', length: 167, cent_start: 57, cent_length: 8 },
       {name: '18', length: 162, cent_start: 46, cent_length: 8 },
       {name: '19', length: 127, cent_start: 64, cent_length: 8 },
       {name: '20', length: 132, cent_start: 64, cent_length: 8 },
       {name: '21', length: 107, cent_start: 38, cent_length: 8 },
       {name: '22', length: 114, cent_start: 42, cent_length: 8 },
       {name: 'X', length: 305, cent_start: 127, cent_length: 8 },
       {name: 'Y', length: 127, cent_start: 39, cent_length: 4 }]


/**
 * Iterate case.individuals. If a path to a image directory
 * is set, get panels on the page and add image content
 */
function add_image_to_individual_panel(individuals, prefixes, institute, case_name){
    console.log(individuals)
    console.log(prefixes)
    for (var i=0; i<individuals.length; i++){
        if(individuals[i].chromograph_images){            
            draw_tracks(individuals[i], prefixes, institute, case_name)
        }
    }
}


// <svg id="svg_ADM1059A1"> </svg>


/**
 * Draw ROH call pictures -coverage- and UPD pictures -color coded
 * genome regions- onto the dashboard.
 */
function draw_tracks(individual, prefixes, institute, case_name){
    console.log("DRAW TRACKS")
    console.log(individual)
    const CYT_HEIGHT = 50 ;
    const CYT_WIDTH = 500 ;
    var svg_element = document.getElementById("svg_" + individual["individual_id"])
    var roh_imgPath = create_path(institute, case_name, individual, 'roh_images')
    var upd_imgPath = create_path(institute, case_name, individual, 'upd_images')
    var ideo_imgPath = create_path(institute, case_name, individual, 'chr_images')
    console.log("- - -")
    console.log(prefixes)
    console.log(institute)
    console.log(case_name)

    var roh_imgObj = new Image();
    var upd_imgObj = new Image();
    var roh_images = make_names(prefixes.roh);
    var upd_images = make_names(prefixes.upd);
    var ideo_images = make_names(prefixes.chr);
    var number_of_columns = $(window).width() < WIDTH_BREAKPOINT? 2:3
    var chromspecs_list
    console.log(roh_images)
    chromspecs_list = get_chromosomes(individual.sex)
    console.log("***")
    console.log(svg_element)
    console.log("svg_" + individual["individual_id"])
   
    for(i = 0; i< chromspecs_list.length; i++){
        roh_imgObj.src = roh_imgPath + roh_images[i]
        upd_imgObj.src = upd_imgPath + upd_images[i]
        x_pos = i % number_of_columns == 0? 0 : CYT_WIDTH * (i% number_of_columns) + OFFSET_X
        y_pos =  Math.floor( i/number_of_columns ) * 100;

        var g = document.createElementNS('http://www.w3.org/2000/svg','g');
        var ideo_image = make_svgimage(ideo_imgPath + ideo_images[i],
                                       x_pos,
                                       y_pos,
                                       "25px", "500px", );

        var upd_image = make_svgimage(upd_imgPath + upd_images[i],
                                      x_pos,
                                      y_pos + 30,
                                      "25px", "500px", );

        var roh_image = make_svgimage(roh_imgPath + roh_images[i],
                                      x_pos + 17,  // compensate for image pixel start
                                      y_pos + 55 , // place below UPD
                                      "25px", "500px", );


        var t = chromosome_text(CHROMOSOMES[i], x_pos, y_pos+17);
        var clipPath = make_clipPath(CHROMSPECS_LIST[i], x_pos, y_pos)
        ideo_image.setAttributeNS(null, 'clip-path', "url(#clip-chr"+CHROMSPECS_LIST[i].name +")")

        g.appendChild(roh_image);
        g.appendChild(upd_image);
        g.appendChild(ideo_image);
        g.appendChild(clipPath);
        g.appendChild(t);

        svg_element.append(g)
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
 * Draw ROH call pictures -coverage- and UPD pictures -color coded
 * genome regions- onto the dashboard. Return a list of names.
 */
function make_names(prefix){
    var names = [];
    for (var i = 0; i < CHROMOSOMES.length; i++){
        id = CHROMOSOMES[i];
        names[i] = prefix+id+".png";
    }
    return names;
}


/**
 *
 *
 */
function chromosome_text(text, x, y){
    var t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    t.setAttributeNS(null, 'x', x+5);
    t.setAttributeNS(null, 'y', y);
    t.appendChild( document.createTextNode(text) );
    return t;
}


// Male
function get_chromosomes(sex){
    if(sex=="1"){
        
        return CHROMSPECS_LIST}
    else{
        return CHROMSPECS_LIST.slice(0, CHROMSPECS_LIST.length-1)}
    }



/**
 *
 *
 */
function make_clipPath(chrom, x_offset, y_offset){
    const c = 10
    var defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    var clipPath = document.createElementNS('http://www.w3.org/2000/svg', 'clipPath');
    clipPath.setAttributeNS(null, 'id', "clip-chr"+chrom.name)
    var p1 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
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
    var r = 10
    var cent_l = calc_centromere_lower(start_l)
    var b_left = "L " + " " + String( 30 + x_offset) + " " + String(y_offset + 25) + " "
    var c1 = "C " + " " + String(30 - r + x_offset) + " " + String(25 + y_offset) + " "
        + String(30 - r + x_offset) + " " + String(y_offset) + " "
        + String(30 + x_offset) + " " + String( y_offset) + " "

    var cent_u = calc_centromere_upper(start_u)
    var right = "L " + String(chrom.length + x_offset) + " " + String(y_offset) + " "

    var c2 = "C " + " " + String(chrom.length + r + x_offset) + " " + String(y_offset) + " "
        + String(chrom.length + r + x_offset) + " " + String(y_offset+25) + " "
        + String(chrom.length + x_offset) + " " + String( y_offset+25)+ " "

    path = m + cent_l + b_left + c1 + cent_u + right + c2

    // without_cent = start +  b_left + c1 + right + c2
    p1.setAttributeNS(null, 'd', path)
    // p1.setAttributeNS(null, 'd', "M 470 25 L 60 25 C 50 25 50 0 60 0 L 470 0 C 510 0 510 25 470 25");

    clipPath.append(p1)
    defs.append(clipPath)
    return clipPath
}



/**
 *
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
    // console.log("upper centromere: %s ", l1 + l2 + l3 + l4);
    return l1 + l2 + l3 + l4
}


/**
 *
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
    // console.log("lower centromere: %s ", l1 + l2 + l3 + l4);
    return l1 + l2 + l3 + l4
}


/**
 *
 *
 */
function make_svgimage(src, x, y, height, width){
    var svgimg = document.createElementNS('http://www.w3.org/2000/svg','image');
    svgimg.setAttributeNS('http://www.w3.org/1999/xlink','href', src);
    svgimg.setAttributeNS(null, 'x', String(x));
    svgimg.setAttributeNS(null, 'y', String(y));
    svgimg.setAttributeNS(null, 'height', String(height));
    svgimg.setAttributeNS(null, 'width', String(width));

    // svgimg.setAttributeNS(null, 'clip-path', "url(#left)");
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


/**
 *
 *
 */
function urlExists(url){
    var http = new XMLHttpRequest();
    http.open('HEAD', url, false);
    http.send();
    return http.status!=404;
}


/**
 *
 *
 */
function getSex(individuals){
    for (var i=0; i<individuals.length; i++){
        if(individuals[i].phenotype == 2){
            if(individuals[i].sex == 1){
                return 'xy'
            }
            if(individuals[i].sex == 2){
                return 'xx'
            }
        }
    }
    return false
}


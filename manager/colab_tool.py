import io
import json
import uuid
import base64
import numpy as np
from PIL import Image
from google.colab import output
from google.colab.output import eval_js
from typing import Dict, List, Union
from IPython.display import display, Javascript


def image_from_numpy(image):
    with io.BytesIO() as img_output:
        Image.fromarray(image).save(img_output, format='JPEG')
        data = img_output.getvalue()
    data = str(base64.b64encode(data))[2:-1]
    return data


def draw_square_one(image_urls, callbackId):
    js = Javascript('''
              async function load_image(imgs, callbackId) {
                  //init organizational elements
                  const div = document.createElement('div');
                  var image_cont = document.createElement('div');
                  var errorlog = document.createElement('div');
                  var crosshair_h = document.createElement('div');
                  crosshair_h.style.position = "absolute";
                  crosshair_h.style.backgroundColor = "transparent";
                  crosshair_h.style.width = "100%";
                  crosshair_h.style.height = "0px";
                  crosshair_h.style.zIndex = 9998;
                  crosshair_h.style.borderStyle = "dotted";
                  crosshair_h.style.borderWidth = "2px";
                  crosshair_h.style.borderColor = "rgba(255, 0, 0, 0.75)";
                  crosshair_h.style.cursor = "crosshair";
                  var crosshair_v = document.createElement('div');
                  crosshair_v.style.position = "absolute";
                  crosshair_v.style.backgroundColor = "transparent";
                  crosshair_v.style.width = "0px";
                  crosshair_v.style.height = "100%";
                  crosshair_v.style.zIndex = 9999;
                  crosshair_v.style.top = "0px";
                  crosshair_v.style.borderStyle = "dotted";
                  crosshair_v.style.borderWidth = "2px";
                  crosshair_v.style.borderColor = "rgba(255, 0, 0, 0.75)";
                  crosshair_v.style.cursor = "crosshair";
                  crosshair_v.style.marginTop = "23px";
                  var brdiv = document.createElement('br');

                  //init control elements
                  var next = document.createElement('button');
                  var prev = document.createElement('button');
                  var submit = document.createElement('button');
                  
                  //init image containers
                  var image = new Image();
                  var canvas_img = document.createElement('canvas');
                  var ctx = canvas_img.getContext("2d");
                  canvas_img.style.cursor = "crosshair";
                  canvas_img.setAttribute('draggable', false);
                  crosshair_v.setAttribute('draggable', false);
                  crosshair_h.setAttribute('draggable', false);

                  // bounding box containers
                  var allBoundingBoxes = [];
                  var curr_image = 0;
                  var im_height = 0;
                  var im_width = 0;

                  //initialize image view
                  errorlog.id = 'errorlog';
                  image.style.display = 'block';
                  image.setAttribute('draggable', false);

                  //load the first image
                  img = imgs[curr_image];
                  image.src = "data:image/png;base64," + img;
                  image.onload = function() {
                      // normalize display height and canvas
                      image_cont.height = canvas_img.height = image.naturalHeight;
                      image_cont.width = canvas_img.width = image.naturalWidth;
                      crosshair_v.style.height = image_cont.height + "px";
                      crosshair_h.style.width = image_cont.width + "px";

                      // draw the new image
                      ctx.drawImage(image, 0, 0, image.naturalWidth, image.naturalHeight, 0, 0,  canvas_img.width,  canvas_img.height);

                  };

                  // move to next image in array
                  next.textContent = "Next";
                  next.onclick = function(){
                      if (curr_image < imgs.length - 1){
                          // clear canvas and load new image
                          curr_image += 1;
                          errorlog.innerHTML = "";
                      }
                      else{
                          errorlog.innerHTML = "All images completed!!";
                      }
                      resetcanvas();
                  }

                  // move forward through list of images
                  prev.textContent = "Previous"
                  prev.onclick = function(){
                      if (curr_image > 0){
                          // clear canvas and load new image
                          curr_image -= 1;
                          errorlog.innerHTML = "";
                      }
                      else{
                          errorlog.innerHTML = "at the beginning";
                      }
                      resetcanvas();
                  }

                  // on submit, send the boxes to display
                  submit.textContent = "submit";
                  submit.onclick = function(){
                    errorlog.innerHTML = "";

                    // send box data to callback fucntion
                    google.colab.kernel.invokeFunction(callbackId, [allBoundingBoxes], {});
                  }

                // init template for annotations
                const annotation = {x: 0, y: 0, w: 0, h: 0, };

                // the array of all rectangles
                let boundingBoxes = allBoundingBoxes;

                // the actual rectangle, the one that is being drawn
                let o = {};

                // a variable to store the mouse position
                let m = {},

                // a variable to store the point where you begin to draw the rectangle
                start = {};

                // a boolean variable to store the drawing state
                let isDrawing = false;
                var elem = null;

                function handleMouseDown(e) {
                  // clear history
                  boundingBoxes.pop();
                  
                  ctx.clearRect(0, 0, canvas_img.width, canvas_img.height);
                  image.src = "data:image/png;base64," + img;
                  image.onload = function() {
                        ctx.drawImage(image, 0, 0, image.naturalWidth, image.naturalHeight, 0, 0,  canvas_img.width,  canvas_img.height);
                        boundingBoxes.map(r => {drawRect(r)});
                  };

                  // on mouse click set change the cursor and start tracking the mouse position
                  start = oMousePos(canvas_img, e);

                  // configure is drawing to true
                  isDrawing = true;
                }

                function handleMouseMove(e) {
                    // move crosshairs, but only within the bounds of the canvas
                    if (document.elementsFromPoint(e.pageX, e.pageY).includes(canvas_img)) {
                      crosshair_h.style.top = e.pageY + "px";
                      crosshair_v.style.left = e.pageX + "px";
                    }

                    // move the bounding box
                    if(isDrawing){
                      m = oMousePos(canvas_img, e);
                      draw_box();
                    }
                }

                function handleMouseUp(e) {
                    if (isDrawing) {
                        // on mouse release, push a bounding box to array and draw_box all boxes
                        isDrawing = false;

                        const box = Object.create(annotation);

                        // calculate the position of the rectangle
                        if (o.w > 0){
                          box.x = o.x;
                        }
                        else{
                          box.x = o.x + o.w;
                        }
                        if (o.h > 0){
                          box.y = o.y;
                        }
                        else{
                          box.y = o.y + o.h;
                        }
                        box.w = Math.abs(o.w);
                        box.h = Math.abs(o.h);

                        // add the bounding box to the image
                        boundingBoxes.push(box);
                        
                        draw_box();
                    }
                }

                function draw_box() {
                    o.x = (start.x)/image.width;  // start position of x
                    o.y = (start.y)/image.height;  // start position of y
                    o.w = Math.max(m.x - start.x, m.y - start.y)/image.width;  // width
                    o.h = Math.max(m.x - start.x, m.y - start.y)/image.height;  // height

                    ctx.clearRect(0, 0, canvas_img.width, canvas_img.height);
                    ctx.drawImage(image, 0, 0, image.naturalWidth, image.naturalHeight, 0, 0,  canvas_img.width,  canvas_img.height);
                    // draw all the rectangles saved in the rectsRy
                    boundingBoxes.map(r => {drawRect(r)});
                    
                    // draw the actual rectangle
                    drawRect(o);
                }

                // add the handlers needed for dragging
                crosshair_h.addEventListener("mousedown", handleMouseDown);
                crosshair_v.addEventListener("mousedown", handleMouseDown);
                document.addEventListener("mousemove", handleMouseMove);
                document.addEventListener("mouseup", handleMouseUp);

                function resetcanvas(){
                    // clear canvas
                    ctx.clearRect(0, 0, canvas_img.width, canvas_img.height);
                    img = imgs[curr_image]
                    image.src = "data:image/png;base64," + img;

                    // onload init new canvas and display image
                    image.onload = function() {
                        // normalize display height and canvas
                        image_cont.height = canvas_img.height = image.naturalHeight;
                        image_cont.width = canvas_img.width = image.naturalWidth;
                        crosshair_v.style.height = image_cont.height + "px";
                        crosshair_h.style.width = image_cont.width + "px";

                        // draw the new image
                        ctx.drawImage(image, 0, 0, image.naturalWidth, image.naturalHeight, 0, 0,  canvas_img.width,  canvas_img.height);

                        // draw bounding boxes
                        boundingBoxes.map(r => {drawRect(r)});
                    };
                }

                function drawRect(o){
                    // draw a predefined rectangle
                    ctx.strokeStyle = "blue";
                    ctx.lineWidth = 3;
                    ctx.beginPath(o);
                    ctx.rect(o.x * image.width, o.y * image.height, o.w * image.width, o.h * image.height);
                    ctx.stroke();
                }

                // Function to detect the mouse position
                function oMousePos(canvas_img, evt) {
                  let ClientRect = canvas_img.getBoundingClientRect();
                    return {
                      x: evt.clientX - ClientRect.left,
                      y: evt.clientY - ClientRect.top
                    };
                }


                //configure colab output display
                google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);

                //build the html document that will be seen in output
                div.appendChild(document.createElement('br'))
                div.appendChild(image_cont)
                image_cont.appendChild(canvas_img)
                image_cont.appendChild(crosshair_h)
                image_cont.appendChild(crosshair_v)
                div.appendChild(document.createElement('br'))
                div.appendChild(errorlog)
                div.appendChild(prev)
                div.appendChild(next)
                div.appendChild(document.createElement('br'))
                div.appendChild(brdiv)
                div.appendChild(submit)
                document.querySelector("#output-area").appendChild(div);
                return
            }''')

    # load the images as a byte array
    bytearrays = []
    for image in image_urls:
        if isinstance(image, np.ndarray):
            bytearrays.append(image_from_numpy(image))
        else:
            raise TypeError(
                'Image has unsupported type {}.'.format(type(image)))

    # format arrays for input
    image_data = json.dumps(bytearrays)
    del bytearrays

    # call java script function pass string byte array(image_data) as input
    display(js)
    eval_js('load_image({}, \'{}\')'.format(image_data, callbackId))
    return


def annotate_square_one(imgs: List[Union[str, np.ndarray]],
                        box_storage_pointer: List[np.ndarray],
                        callbackId: str = None):
    # Set a random ID for the callback function
    if callbackId is None:
        callbackId = str(uuid.uuid1()).replace('-', '')

    def dictToList(input_bbox):
        return (input_bbox['y'], input_bbox['x'], input_bbox['y'] + input_bbox['h'], input_bbox['x'] + input_bbox['w'])

    def callbackFunction(annotations: List[Dict[str, float]]):
        # reset the boxes list
        nonlocal box_storage_pointer
        boxes: List[np.ndarray] = box_storage_pointer
        boxes.clear()

        rectangles_as_arrays = [
            np.clip(dictToList(annotation), 0, 1) for annotation in annotations]
        if rectangles_as_arrays:
            boxes.append(np.stack(rectangles_as_arrays))
        else:
            boxes.append(None)

        # output the annotations to the errorlog
        with output.redirect_to_element('#errorlog'):
            display('--boxes array populated--')

    output.register_callback(callbackId, callbackFunction)
    draw_square_one(imgs, callbackId)

macro make_thumbnail{

	imageUrl = getArgument();
	dotIndex = indexOf(imageUrl, ".");
    title = substring(imageUrl, 0, dotIndex); 
	outputUrl = title + "_thumb.jpg"
	miniatureHeight = 64;

	process(imageUrl, miniatureHeight, outputUrl);

}

function process(imageUrl, miniatureHeight, outputUrl){
	
	open(imageUrl);

	// convert to 8 bits if needed
	imageDepth = bitDepth();
	if (imageDepth == 16 || imageDepth == 32){
		run("8-bit");
	}
	
	// resize image
	getDimensions(width, height, channels, slices, frames);

	if (frames > 1){
		run("Duplicate...", "duplicate frames=1");
	}
	
	if (slices > 1){
		run("Z Project...", "projection=[Max Intensity]");
	}

	if (channels > 1){
		run("Stack to RGB");
	}

	if (height > miniatureHeight){
		run("Scale...", "x=- y=- width="+miniatureHeight+" height="+miniatureHeight+" interpolation=Bilinear average create");
	}
	saveAs("jpg", outputUrl);
	run("Close All");
}

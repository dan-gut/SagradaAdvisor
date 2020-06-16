/*

Abstract:
Main view controller for the AR experience.
*/

import ARKit
import SceneKit
import UIKit
import Vision


class ViewController: UIViewController, ARSCNViewDelegate {
    var gameSession: GameSession?
    var dieState:[Die] = Array(repeating: Die(num: 0, color: .none), count: 4) {
        didSet {
            //update display
            
            for (i, s) in dieState.enumerated() {
                let dieView = view.subviews.first { $0.tag - 1 == i } as? UIButton
                dieView?.backgroundColor = s.color.systemColor()
                dieView?.setTitle(String(s.num), for: .normal)
                
            }
        }
    }
    var text: SCNText?
    var planeNode: SCNNode?
    var diceCardNodes = [CardWithDice]()
    @IBAction func changeNumber(_ sender: UIButton) {
        let newVal = dieState[sender.tag-1].num + 1
        dieState[sender.tag-1].num = (newVal == 7) ? 1 : newVal
    }
    @IBAction func changeColor(_ sender: UIButton) {
        dieState[sender.tag-10].color.next()
    }
    
    @IBOutlet var sceneView: ARSCNView!
    
    @IBOutlet weak var blurView: UIVisualEffectView!
    let predictionQueue = DispatchQueue(label: "predictionQueue",
                                        qos: .userInitiated,
                                        attributes: [],
                                        autoreleaseFrequency: .inherit,
                                        target: nil)

    /// The view controller that displays the status and "restart experience" UI.
    lazy var statusViewController: StatusViewController = {
        return childViewControllers.lazy.compactMap({ $0 as? StatusViewController }).first!
    }()
    
    /// A serial queue for thread safety when modifying the SceneKit node graph.
    let updateQueue = DispatchQueue(label: Bundle.main.bundleIdentifier! +
        ".serialSceneKitQueue")
    
    /// Layer used to host detectionOverlay layer
    var rootLayer: CALayer!
    /// The detection overlay layer used to render bounding boxes
    var detectionOverlay: CALayer!
    
    /// Whether the current frame should be skipped (in terms of model predictions)
    var shouldSkipFrame = 0
    /// How often (in terms of camera frames) should the app run predictions
    let predictEvery = 10
    
    /// Vision request for the detection model
    var diceDetectionRequest: VNCoreMLRequest!
    
    /// Flag used to decide whether to draw bounding boxes for detected objects
    var showBoxes = true {
        didSet {
            if !showBoxes {
                removeBoxes()
            }
        }
    }
    
    /// Size of the camera image buffer (used for overlaying boxes)
    var bufferSize: CGSize! {
        didSet {
            if bufferSize != nil {
                if oldValue == nil {
                    setupLayers()
                } else if oldValue != bufferSize {
                    updateDetectionOverlaySize()
                }
            }
            
        }
    }
    
    /// The last known image orientation
    /// When the image orientation changes, the buffer size used for rendering boxes needs to be adjusted
    var lastOrientation: CGImagePropertyOrientation = .right
    
    /// Last known dice values
    var lastDiceValues = [Int]()
    /// last observed dice
    var lastObservations = [VNRecognizedObjectObservation]()
    var performedMoves = [String]()

    /// Convenience accessor for the session owned by ARSCNView.
    var session: ARSession {
        return sceneView.session
    }
    
    // MARK: - View Controller Life Cycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        sceneView.delegate = self
        sceneView.session.delegate = self
        sceneView.automaticallyUpdatesLighting = true
        sceneView.autoenablesDefaultLighting = true
        // Hook up status view controller callback(s).
        statusViewController.restartExperienceHandler = { [unowned self] in
            self.restartExperience()
        }
        rootLayer = sceneView.layer
        guard let detector = try? VNCoreMLModel(for: DiceDetector().model) else {
            print("Failed to load detector!")
            return
        }
        detector.featureProvider = ThresholdProvider()
        diceDetectionRequest = VNCoreMLRequest(model: detector) { [weak self] request, error in
            self?.detectionRequestHandler(request: request, error: error)
        }
        // .scaleFill results in a slight skew but the model was trained accordingly
        // see https://developer.apple.com/documentation/vision/vnimagecropandscaleoption for more information
        diceDetectionRequest.imageCropAndScaleOption = .scaleFill
        let tap = UITapGestureRecognizer(target: self, action: #selector(search))
        self.sceneView.addGestureRecognizer(tap)

    }

	override func viewDidAppear(_ animated: Bool) {
		super.viewDidAppear(animated)
		
		// Prevent the screen from being dimmed to avoid interuppting the AR experience.
		UIApplication.shared.isIdleTimerDisabled = true

        // Start the AR experience
        resetTracking()
	}
	
	override func viewWillDisappear(_ animated: Bool) {
		super.viewWillDisappear(animated)

        session.pause()
	}
    @IBAction func detectDicePressed(_ sender: Any) {
        guard let frame = session.currentFrame else {
            print("error")
            return
        }
        guard let _ = gameSession else {
            let alert = UIAlertController(title: "First point to a board and start game", message: nil, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "Ok", style: .cancel, handler: nil))
            present(alert, animated: true, completion: nil)
            return
        }
        
        if shouldSkipFrame > 0 {
            shouldSkipFrame = (shouldSkipFrame + 1) % predictEvery
        }
        
        predictionQueue.async {
            /// - Tag: MappingOrientation
            // The frame is always oriented based on the camera sensor,
            // so in most cases Vision needs to rotate it for the model to work as expected.
            let orientation = UIDevice.current.orientation
            
            // The image captured by the camera
            let image = frame.capturedImage
            
            let imageOrientation: CGImagePropertyOrientation
            switch orientation {
            case .portrait:
                imageOrientation = .right
            case .portraitUpsideDown:
                imageOrientation = .left
            case .landscapeLeft:
                imageOrientation = .up
            case .landscapeRight:
                imageOrientation = .down
            case .unknown:
                //                print("The device orientation is unknown, the predictions may be affected")
                fallthrough
            default:
                // By default keep the last orientation
                // This applies for faceUp and faceDown
                imageOrientation = self.lastOrientation
            }
            
            // For object detection, keeping track of the image buffer size
            // to know how to draw bounding boxes based on relative values.
            if self.bufferSize == nil || self.lastOrientation != imageOrientation {
                self.lastOrientation = imageOrientation
                let pixelBufferWidth = CVPixelBufferGetWidth(image)
                let pixelBufferHeight = CVPixelBufferGetHeight(image)
                if [.up, .down].contains(imageOrientation) {
                    self.bufferSize = CGSize(width: pixelBufferWidth,
                                             height: pixelBufferHeight)
                } else {
                    self.bufferSize = CGSize(width: pixelBufferHeight,
                                             height: pixelBufferWidth)
                }
            }
            /// - Tag: PassingFramesToVision
            
            let ciImage = CIImage(cvPixelBuffer: image)
            let filterInvert = CIFilter(name: "CIColorInvert")!
            filterInvert.setValue(ciImage, forKey: kCIInputImageKey)
            let result1 = filterInvert.outputImage!
            
            let filterColor = CIFilter(name: "CIColorControls")!
            filterColor.setValue(result1, forKey: kCIInputImageKey)
            filterColor.setValue(0.0, forKey: kCIInputBrightnessKey)
            filterColor.setValue(0.0, forKey: kCIInputSaturationKey)
            filterColor.setValue(1.1, forKey: kCIInputContrastKey)
            
            let result2 = filterColor.outputImage
            
            let filterExposure = CIFilter(name:"CIExposureAdjust")!
            filterExposure.setValue(result2, forKey: kCIInputImageKey)
            filterExposure.setValue(0.7, forKey: kCIInputEVKey)
            let output = filterExposure.outputImage!
            
            //            let context = CIContext()
            //            context.render(output, to: image)
            //
            //            let processed_image = output.pixelBuffer!
            
            // Invoke a VNRequestHandler with that image
            //            let handler = VNImageRequestHandler(cvPixelBuffer: image, orientation: imageOrientation, options: [:])
            let handler = VNImageRequestHandler(ciImage: output, orientation: imageOrientation, options: [:])
            
            do {
                try handler.perform([self.diceDetectionRequest])
            } catch {
                print("CoreML request failed with error: \(error.localizedDescription)")
            }
            
        }
        
    }
    @IBAction func calculateMove(_ sender: Any) {
        guard let gSession = gameSession else {
            let alert = UIAlertController(title: "First point to a board and start game", message: nil, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "Ok", style: .cancel, handler: nil))
            present(alert, animated: true, completion: nil)
            return
        }
        if !dieState.allSatisfy({$0.valid}){
            let alert = UIAlertController(title: "Set color and value to all your dice", message: nil, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "Ok", style: .cancel, handler: nil))
            present(alert, animated: true, completion: nil)
            return
        }
        gSession.sendDice(diceState: dieState) { (moves) in
            for move in moves {
                self.diceCardNodes.forEach { $0.makeMove(moveCode: move) }
            }
            self.performedMoves.append(contentsOf: moves)
        }
    }
    
    // MARK: - Session management (Image detection setup)
    
    /// Prevents restarting the session while a restart is in progress.
    var isRestartAvailable = true

    /// Creates a new AR configuration to run on the `session`.
    /// - Tag: ARReferenceImage-Loading
	func resetTracking() {
        
        guard let referenceImages = ARReferenceImage.referenceImages(inGroupNamed: "AR Plansze", bundle: nil) else {
            fatalError("Missing expected asset catalog resources.")
        }
        
        let configuration = ARImageTrackingConfiguration()
        configuration.trackingImages = referenceImages
        configuration.isLightEstimationEnabled = true
        
        
        session.run(configuration, options: [.resetTracking, .removeExistingAnchors])

        statusViewController.scheduleMessage("Look around to detect images", inSeconds: 7.5, messageType: .contentPlacement)
	}

    // MARK: - ARSCNViewDelegate (Image detection results)
    /// - Tag: ARImageAnchor-Visualizing
    func renderer(_ renderer: SCNSceneRenderer, didAdd node: SCNNode, for anchor: ARAnchor) {
        guard let imageAnchor = anchor as? ARImageAnchor else { return }
        let referenceImage = imageAnchor.referenceImage
        updateQueue.async {
            
            // Create a plane to visualize the initial position of the detected image.
            let plane = SCNPlane(width: referenceImage.physicalSize.width,
                                 height: referenceImage.physicalSize.height)
            plane.firstMaterial?.diffuse.contents = UIColor.red.cgColor
            let planeNode = SCNNode(geometry: plane)
            planeNode.name = referenceImage.name
            planeNode.opacity = 0.8
            
            let instruction = self.gameSession==nil ? "Tap to start playing \(referenceImage.name ?? "")" : "Scan your dice"

            let text = SCNText(string: instruction, extrusionDepth: 0)
            
            text.firstMaterial?.diffuse.contents = UIColor.white.cgColor
            text.font = UIFont.systemFont(ofSize: 20)
            let textNode = SCNNode(geometry: text)
            self.text = text
            textNode.eulerAngles.x = -.pi / 2
            textNode.scale = SCNVector3Make(0.0003, 0.0003, 0.0003)
            textNode.position.x -= Float(referenceImage.physicalSize.width/2.0)
            textNode.position.z -= Float(referenceImage.physicalSize.height/2.0)
            textNode.position.y += 0.001
            
            let dice = CardWithDice()
            dice.position.x = -Float(referenceImage.physicalSize.width/2)
            dice.position.z = -Float(referenceImage.physicalSize.height/2)
            node.addChildNode(dice)
            self.diceCardNodes.append(dice)
            self.performedMoves.forEach { (move) in
                dice.makeMove(moveCode: move)
            }

            
            /*
             `SCNPlane` is vertically oriented in its local coordinate space, but
             `ARImageAnchor` assumes the image is horizontal in its local space, so
             rotate the plane to match.
             */
            planeNode.eulerAngles.x = -.pi / 2
            
            /*
             Image anchors are not tracked after initial detection, so create an
             animation that limits the duration for which the plane visualization appears.
             */
            
            // Add the plane visualization to the scene.
            node.addChildNode(planeNode)
            node.addChildNode(textNode)
            self.planeNode = planeNode
        }

        DispatchQueue.main.async {
            let imageName = referenceImage.name ?? ""
            self.statusViewController.cancelAllScheduledMessages()
            self.statusViewController.showMessage("Detected image “\(imageName)”")
        }
    }

    @objc func search(sender: UITapGestureRecognizer) {
        
        let sceneView = sender.view as! ARSCNView
        let location = sender.location(in: sceneView)
        let results = sceneView.hitTest(location, options: [SCNHitTestOption.searchMode : 1])
        
        guard sender.state == .ended else { return }
        performedMoves = [];
        
        if let result = results.filter( { ($0.node.geometry?.isKind(of: SCNPlane.self) ) ?? false }).first {
            // start playing
            print("Start playing", result.node.name)
            if let name = result.node.name {
                GameSession.createNewSession(boardName: name) { (session) in
                    self.gameSession = session
                    self.text?.string = "Scan your dice"
                }

            }
        }
    }


}

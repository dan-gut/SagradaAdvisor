//
//  ViewController+Vision.swift
//  ARKitImageDetection
//
//  Created by Piotr Knapczyk on 14/05/2020.
//

import Foundation
import Vision
extension ViewController {
    
    
    //MARK: - Detection
    
    func bounds(for observation: VNRecognizedObjectObservation) -> CGRect {
        let boundingBox = observation.boundingBox
        // Coordinate system is like macOS, origin is on bottom-left and not top-left
        
        // The resulting bounding box from the prediction is a normalized bounding box with coordinates from bottom left
        // It needs to be flipped along the y axis
        let fixedBoundingBox = CGRect(x: boundingBox.origin.x,
                                      y: 1.0 - boundingBox.origin.y - boundingBox.height,
                                      width: boundingBox.width,
                                      height: boundingBox.height)
        
        // Return a flipped and scaled rectangle corresponding to the coordinates in the sceneView
        return VNImageRectForNormalizedRect(fixedBoundingBox, Int(sceneView.frame.width), Int(sceneView.frame.height))
    }
    
    // MARK: - Vision Callbacks
    
    /// Handles results from the detection requests
    ///
    /// - parameters:
    ///     - request: The VNRequest that has been processed
    ///     - error: A potential error that may have occurred
    func detectionRequestHandler(request: VNRequest, error: Error?) {
        // Perform several error checks before proceeding
        if let error = error {
            print("An error occurred with the vision request: \(error.localizedDescription)")
            return
        }
        guard let request = request as? VNCoreMLRequest else {
            print("Vision request is not a VNCoreMLRequest")
            return
        }
        guard let observations = request.results as? [VNRecognizedObjectObservation] else {
            print("Request did not return recognized objects: \(request.results?.debugDescription ?? "[No results]")")
            return
        }
        
        guard !observations.isEmpty else {
            removeBoxes()
            lastObservations = []
            lastDiceValues = []
            // Since there are no detected dice, the roll is in .other state
//            rollState = .other
            return
        }
        
//        if showBoxes && rollState != .ended {
//            drawBoxes(observations: observations)
//        }
        
        // Since there are dice, the roll is either in the .started or .ended state
        
//        if rollState == .ended {
            /// - Tag : SortingDiceObservations
        var sortableDiceValues = [(value: Int, xPosition: CGFloat)]()
        
        for observation in observations {
            // Select only the label with the highest confidence.
            guard let topLabelObservation = observation.labels.first else {
                print("Object observation has no labels")
                continue
            }
            
            if let intValue = Int(topLabelObservation.identifier) {
                sortableDiceValues.append((value: intValue, xPosition: observation.boundingBox.midX))
            }
        }
        
        let diceValues = sortableDiceValues.sorted { $0.xPosition < $1.xPosition }.map { $0.value }
        DispatchQueue.main.async {
            for i in 0..<4 {
                
                if let x = diceValues[safe: i] {
                    self.dieState[i].num = x
                }
            }

        }
//        }
    }
    
}

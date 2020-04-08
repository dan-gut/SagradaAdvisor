//
//  DiceNode.swift
//  ARKitImageDetection
//
//  Created by Piotrek on 08/04/2020.
//  Copyright © 2020 Apple. All rights reserved.
//

import SceneKit




class DiceNode: SCNNode {
    let diceSize:CGFloat = 0.009
    init(number: Int, color: UIColor) {
        super.init()
        let cube = SCNBox(width: diceSize, height: diceSize, length: diceSize, chamferRadius: diceSize/10.0)
        geometry = cube
        cube.firstMaterial?.diffuse.contents = color.cgColor
        cube.firstMaterial?.metalness.contents = NSNumber(value: 0.33)
        cube.firstMaterial?.roughness.contents = NSNumber(value: 0.33)

        cube.firstMaterial?.lightingModel = .physicallyBased
        
        switch number {
        case 1:
            self.addChildNode(dot(0,0))
        case 2:
            self.addChildNode(dot(1,1))
            self.addChildNode(dot(-1,-1))
        case 3:
            self.addChildNode(dot(0,0))
            self.addChildNode(dot(1,1))
            self.addChildNode(dot(-1,-1))
        case 4:
            self.addChildNode(dot(1,-1))
            self.addChildNode(dot(1,1))
            self.addChildNode(dot(-1,1))
            self.addChildNode(dot(-1,-1))
        case 5:
            self.addChildNode(dot(0,0))
            self.addChildNode(dot(1,-1))
            self.addChildNode(dot(1,1))
            self.addChildNode(dot(-1,1))
            self.addChildNode(dot(-1,-1))
        case 6:
            self.addChildNode(dot(1,-1))
            self.addChildNode(dot(1,1))
            self.addChildNode(dot(-1,1))
            self.addChildNode(dot(-1,-1))
            self.addChildNode(dot(-1,0))
            self.addChildNode(dot(1,0))

        default:
            fatalError("Number on dice has to be between 1 and 6")
        }
    }
    func dot(_ x: Int, _ y: Int) -> SCNNode {
        let dotNode = SCNNode(geometry: SCNSphere(radius: diceSize/10))
        dotNode.geometry?.firstMaterial?.diffuse.contents = UIColor.white
        dotNode.position.y = Float(diceSize/2)
        dotNode.position.x = Float(diceSize/4) * Float(x)
        dotNode.position.z = Float(diceSize/4) * Float(y)

        return dotNode
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
}

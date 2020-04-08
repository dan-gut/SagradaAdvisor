//
//  CardWithDice.swift
//  ARKitImageDetection
//
//  Created by Piotrek on 08/04/2020.
//  Copyright © 2020 Apple. All rights reserved.
//

import SceneKit

class CardWithDice: SCNNode {
    let margin:CGFloat = 0.0005
    let offsetX:Float = 0.0015
    let offsetY:Float = 0.0018
    
    let testColors = [UIColor.red, UIColor.blue, UIColor.green, UIColor.purple, UIColor.yellow, UIColor.orange];
    
    override init() {
        super.init()
        for x in 0..<5 {
            for y in 0..<4 {
                let die = DiceNode(number: Int.random(in: 1...6), color: testColors.randomElement()!)
                die.position.x = Float(x) * Float((die.diceSize + margin)) + Float(die.diceSize/2) + offsetX
                die.position.z = Float(y) *  Float((die.diceSize + margin)) + Float(die.diceSize/2) + offsetY
                self.addChildNode(die)
            }
        }
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

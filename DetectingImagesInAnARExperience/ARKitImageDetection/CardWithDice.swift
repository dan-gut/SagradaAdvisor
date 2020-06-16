//
//  CardWithDice.swift
//  ARKitImageDetection
//
//  Created by Piotr Knapczyk on 08/04/2020.
//

import SceneKit

class CardWithDice: SCNNode {
    let margin:CGFloat = 0.0005
    let offsetX:Float = 0.0015
    let offsetY:Float = 0.0018
    
    
    override init() {
        super.init()
    }
    func makeMove(moveCode:String) {
        let codes = moveCode.split(separator: "+")
        let die = String(codes[0])
        let location = Int(codes[1])
        if location == 0 {
            return
        }

        let color = die[0]
        let number = Int(String(die[1]))
        guard let numberO = number, let colorO = Color(rawValue: color) else {
            return
        }
        var count = 1
        for y in 0..<4 {
            for x in 0..<5 {
                    if count == location {
                        let die = DiceNode(number:numberO, color: colorO.systemColor())
                        die.position.x = Float(x) * Float((die.diceSize + margin)) + Float(die.diceSize/2) + offsetX
                        die.position.z = Float(y) *  Float((die.diceSize + margin)) + Float(die.diceSize/2) + offsetY
                        self.addChildNode(die)
                        return
                    }
                    count += 1
            }
        }


        
    }
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

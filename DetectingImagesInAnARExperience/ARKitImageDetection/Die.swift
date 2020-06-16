//
//  Die.swift
//  ARKitImageDetection
//
//  Created by Piotr Knapczyk on 14/05/2020.
//

import Foundation
import UIKit
enum Color:String, CaseIterable {
    case red = "R"
    case blue = "B"
    case green = "G"
    case yellow = "Y"
    case purple = "P"
    case none
    mutating func next() {
        let allCases = type(of: self).allCases
        self = allCases[(allCases.index(of: self)! + 1) % allCases.count]
    }

    func systemColor() -> UIColor {
        switch self {
        case .red:
            return UIColor.red
        case .blue:
            return UIColor.blue
        case .none:
            return UIColor.black
        case .green:
            return UIColor.green
        case .yellow:
            return UIColor.yellow
        case .purple:
            return UIColor.purple
        }
    }
}

struct Die {
    var num: Int
    var color: Color
    var valid: Bool {
        get {
            return color != .none && num >= 1 && num <= 6
        }
    }
    var stringValue: String {
        return color.rawValue+String(num)
    }
}

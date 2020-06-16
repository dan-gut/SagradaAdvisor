//
//  Array+safty.swift
//  ARKitImageDetection
//
//  Created by Piotrek on 14/05/2020.
//  Copyright © 2020 Apple. All rights reserved.
//

import Foundation
extension Collection {
    
    /// Returns the element at the specified index if it is within bounds, otherwise nil.
    subscript (safe index: Index) -> Element? {
        return indices.contains(index) ? self[index] : nil
    }
}
extension String {
    subscript(i: Int) -> String {
        return String(self[index(startIndex, offsetBy: i)])
    }
}

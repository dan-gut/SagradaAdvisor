//
//  GameSession.swift
//  ARKitImageDetection
//
//  Created by Piotrek on 14/05/2020.
//

import Foundation
struct GameSession {
    private let sessionID: String
    private static let root = "http://68.183.211.184:81/"
    init(sessionID: String) {
        self.sessionID = sessionID
    }
    static func createNewSession( boardName:String, sessionCallback: @escaping ((GameSession)->Void)){
        let url = URL(string: GameSession.root+"?name=testname&board_name=\(boardName)&main_mission_color=RED")!
        print(url)
        let task = URLSession.shared.dataTask(with: url) {(data, response, error) in
            guard let data = data, let id = String(data: data, encoding: .utf8) else {
                print("Error loading data", response ?? "", error ?? "")
                return
                
            }
            sessionCallback(GameSession(sessionID: id))
        }
        
        task.resume()

    }
    
    func sendDice(diceState: [Die], callback: @escaping (([String])->Void))  {

        let coded = diceState.map { $0.stringValue }.joined(separator: "+")
        let url = URL(string: GameSession.root+"?game_id=\(sessionID)&dices=\(coded)")!
        print(url)
        let task = URLSession.shared.dataTask(with: url) {(data, response, error) in
            guard let data = data, let moves = String(data: data, encoding: .utf8) else {
                print("Error loading data", response ?? "", error ?? "")
                return
                
            }
            print("response", moves)
            callback(moves.components(separatedBy: "-"))
//            sessionCallback(GameSession(sessionID: id))
        }
        
        task.resume()

    }
}

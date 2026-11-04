import Foundation
import Vision
import AppKit

// Usage: ocr <image.png> [--correct] [--fast] [--boxes]
// --boxes appends width<TAB>height (normalised) after the text, for
// column-aware reading order on prose pages; listing caches omit it.
let args = CommandLine.arguments
guard args.count >= 2, let img = NSImage(contentsOfFile: args[1]),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("cannot open image\n".data(using:.utf8)!); exit(1)
}
let correct = args.contains("--correct")
let fast = args.contains("--fast")
let boxes = args.contains("--boxes")
let req = VNRecognizeTextRequest()
req.recognitionLevel = fast ? .fast : .accurate
req.usesLanguageCorrection = correct     // OFF by default: this is machine code
req.recognitionLanguages = ["en-US"]
req.minimumTextHeight = 0.0
let handler = VNImageRequestHandler(cgImage: cg, options: [:])
do { try handler.perform([req]) } catch {
    FileHandle.standardError.write("perform failed\n".data(using:.utf8)!); exit(1)
}
guard let obs = req.results else { exit(0) }
// emit: y<TAB>x<TAB>confidence<TAB>text   (y from top, so sorting gives reading order)
var lines: [(Double, Double, Float, String, Double, Double)] = []
for o in obs {
    guard let c = o.topCandidates(1).first else { continue }
    let bb = o.boundingBox
    lines.append((1.0 - Double(bb.origin.y) - Double(bb.size.height),
                  Double(bb.origin.x), c.confidence, c.string,
                  Double(bb.size.width), Double(bb.size.height)))
}
lines.sort { $0.0 == $1.0 ? $0.1 < $1.1 : $0.0 < $1.0 }
for l in lines {
    if boxes {
        print(String(format:"%.4f\t%.4f\t%.3f\t%@\t%.4f\t%.4f", l.0, l.1, l.2, l.3, l.4, l.5))
    } else {
        print(String(format:"%.4f\t%.4f\t%.3f\t%@", l.0, l.1, l.2, l.3))
    }
}

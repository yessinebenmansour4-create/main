"""Rebuild Real-ESRGAN realesr-general-x4v3 (SRVGGNetCompact) as ONNX without PyTorch.

Reads the official .pth checkpoints (zip + pickle) with a minimal unpickler, blends the
regular and "wdn" (weak denoise) weights like Real-ESRGAN's --denoise_strength, and writes
an ONNX graph runnable with onnxruntime on CPU.

Usage: python3 scripts/esrgan_onnx.py <x4v3.pth> <wdn-x4v3.pth> <denoise_strength 0..1> <out.onnx>
"""
import pickle, sys, zipfile, collections
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper

DT = {"FloatStorage": np.float32, "HalfStorage": np.float16, "DoubleStorage": np.float64, "LongStorage": np.int64}


def load_pth(path):
    zf = zipfile.ZipFile(path)
    root = zf.namelist()[0].split("/")[0]

    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if mod == "torch._utils" and name == "_rebuild_tensor_v2":
                def rebuild(storage, offset, size, stride, *a, **k):
                    return np.lib.stride_tricks.as_strided(storage[offset:], shape=size,
                                                           strides=[s * storage.itemsize for s in stride]).copy()
                return rebuild
            if mod == "torch" and name.endswith("Storage"):
                return name
            if mod == "collections" and name == "OrderedDict":
                return collections.OrderedDict
            return super().find_class(mod, name)

        def persistent_load(self, pid):
            _, stype, key, _loc, _numel = pid
            stype = stype if isinstance(stype, str) else getattr(stype, "__name__", str(stype))
            return np.frombuffer(zf.read(f"{root}/data/{key}"), dtype=DT[stype])

    obj = U(zf.open(f"{root}/data.pkl")).load()
    return obj.get("params_ema", obj.get("params", obj))


def build(sd, out):
    convs = sorted({int(k.split(".")[1]) for k in sd if k.endswith(".bias")})
    nodes, inits, x = [], [], "input"
    for i, idx in enumerate(convs):
        w, b = sd[f"body.{idx}.weight"].astype(np.float32), sd[f"body.{idx}.bias"].astype(np.float32)
        inits += [numpy_helper.from_array(w, f"w{idx}"), numpy_helper.from_array(b, f"b{idx}")]
        nodes.append(helper.make_node("Conv", [x, f"w{idx}", f"b{idx}"], [f"c{idx}"], pads=[1, 1, 1, 1]))
        x = f"c{idx}"
        if f"body.{idx + 1}.weight" in sd and f"body.{idx + 1}.bias" not in sd:  # PReLU
            a = sd[f"body.{idx + 1}.weight"].astype(np.float32).reshape(-1, 1, 1)
            inits.append(numpy_helper.from_array(a, f"a{idx}"))
            nodes.append(helper.make_node("PRelu", [x, f"a{idx}"], [f"p{idx}"]))
            x = f"p{idx}"
    nodes.append(helper.make_node("DepthToSpace", [x], ["up"], blocksize=4, mode="CRD"))
    inits.append(numpy_helper.from_array(np.array([1, 1, 4, 4], np.float32), "scales"))
    nodes.append(helper.make_node("Resize", ["input", "", "scales"], ["base"], mode="nearest"))
    nodes.append(helper.make_node("Add", ["up", "base"], ["output"]))
    g = helper.make_graph(nodes, "srvgg_x4",
                          [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, "h", "w"])],
                          [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 3, "H", "W"])], inits)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 17)])
    m.ir_version = 9  # readable by onnxruntime 1.2x
    onnx.checker.check_model(m)
    onnx.save(m, out)
    print(f"{out}: {len(convs)} convs")


if __name__ == "__main__":
    a, b, s, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    A, B = load_pth(a), load_pth(b)
    sd = {k: s * A[k].astype(np.float32) + (1 - s) * B[k].astype(np.float32) for k in A}
    build(sd, out)

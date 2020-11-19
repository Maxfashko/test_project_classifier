import cv2


def transform_input_width_height(data):
    frame = data.get("frame")
    args = data.get("args")

    if args.input_width and args.input_height:
        if frame.shape[1] != args.input_width and frame.shape[0] != args.input_height:
            frame = cv2.resize(frame, (args.input_width, args.input_height), interpolation=cv2.INTER_NEAREST,)
    return {"frame": frame, "args": args}


def transform_input_size_scale(data):
    frame = data.get("frame")
    args = data.get("args")

    if args.input_size_scale:
        frame = cv2.resize(
            frame, (0, 0), fy=args.input_size_scale, fx=args.input_size_scale, interpolation=cv2.INTER_NEAREST,
        )
    return {"frame": frame, "args": args}

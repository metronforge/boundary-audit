"""Shared canonical framing for compression and provenance."""

import json
import math
from collections.abc import Mapping

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import SerializationError
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue

MAGIC = b"BAUD"
SERIALIZATION_VERSION = 1
SYMBOL_ID_TAG = b"\x00"
BOUNDARY_TAG = b"\x01"
EXACT_SYMBOL_TAG = b"\x02"


def encode_uleb128(value: int) -> bytes:
    """Encode an arbitrary non-negative Python integer as unsigned LEB128."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SerializationError("ULEB128 values must be non-negative integers")
    output = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            output.append(byte | 0x80)
        else:
            output.append(byte)
            return bytes(output)


def structural_stream_bytes(
    stream: SymbolStream, boundaries: BoundaryConfiguration
) -> bytes:
    """Encode first-observed IDs and structural boundary records."""
    if len(stream) != boundaries.stream_length:
        raise SerializationError("stream and boundary configuration lengths differ")
    alphabet = stream.alphabet()
    ids = {symbol: i for i, symbol in enumerate(alphabet.symbols)}
    positions = set(boundaries.positions)
    output = bytearray(MAGIC)
    output.append(SERIALIZATION_VERSION)
    output.extend(encode_uleb128(alphabet.size))
    for i, symbol in enumerate(stream.symbols):
        output.extend(SYMBOL_ID_TAG)
        output.extend(encode_uleb128(ids[symbol]))
        if i + 1 in positions:
            output.extend(BOUNDARY_TAG)
    return bytes(output)


def exact_stream_bytes(stream: SymbolStream) -> bytes:
    """Frame exact UTF-8 symbol spellings without ambiguous concatenation."""
    output = bytearray(MAGIC)
    output.append(SERIALIZATION_VERSION)
    output.extend(encode_uleb128(len(stream)))
    for symbol in stream.symbols:
        encoded = symbol.encode("utf-8")
        output.extend(EXACT_SYMBOL_TAG)
        output.extend(encode_uleb128(len(encoded)))
        output.extend(encoded)
    return bytes(output)


def boundary_bytes(boundaries: BoundaryConfiguration) -> bytes:
    """Frame stream length and increasing boundary positions."""
    output = bytearray(MAGIC + bytes((SERIALIZATION_VERSION,)))
    output.extend(encode_uleb128(boundaries.stream_length))
    output.extend(encode_uleb128(boundaries.count))
    for position in boundaries.positions:
        output.extend(BOUNDARY_TAG)
        output.extend(encode_uleb128(position))
    return bytes(output)


def canonical_json_bytes(value: Mapping[str, JSONValue]) -> bytes:
    """Encode validated JSON-compatible parameters deterministically."""

    def validate(item: JSONValue) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise SerializationError("NaN and infinity are not canonical JSON values")
        if isinstance(item, list):
            for child in item:
                validate(child)
        elif isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise SerializationError("canonical JSON object keys must be strings")
            for child in item.values():
                validate(child)

    materialized = dict(value)
    validate(materialized)
    try:
        encoded = json.dumps(
            materialized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise SerializationError("value is not canonical JSON serializable") from exc
    return encoded.encode("utf-8")

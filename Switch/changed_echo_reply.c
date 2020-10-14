/* Creates and returns the current time in
 * OFPT_ECHO_REQUEST message in 'rq'. */
struct ofpbuf *
make_echo_reply(const struct ofp_header *rq)
{
struct timespec t;

struct timestamp {
    uint8_t version;    /* OFP_VERSION. */
    uint8_t type;       /* One of the OFPT_ constants. */
    uint16_t length;    /* Length including this ofp_header. */
    uint32_t xid;       /* Transaction id associated with this packet.
                           Replies use the same id as was in the request
                           to facilitate pairing. */
int64_t timestamp;
};

    clock_gettime( CLOCK_REALTIME, &t);

    int64_t ts =
    (int64_t)(t.tv_sec) * (int64_t)1000000000 + (int64_t)(t.tv_nsec);

    struct timestamp * tmp = rq;
    tmp->timestamp=ts;

    struct ofpbuf rq_buf = ofpbuf_const_initializer(rq, ntohs(rq->length));

    ofpraw_pull_assert(&rq_buf);

    struct ofpbuf *reply = ofpraw_alloc_reply(OFPRAW_OFPT_ECHO_REPLY,
                                              rq, rq_buf.size);

    ofpbuf_put(reply, rq_buf.data, rq_buf.size);

    return reply;
}

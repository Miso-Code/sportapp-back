from app.models.schemas.schema import UserTraining, AdverseIncidentBoundingBox


def is_user_in_bounding_box(user: UserTraining, bounding_box: AdverseIncidentBoundingBox):
    return bounding_box.latitude_from <= user.latitude <= bounding_box.latitude_to and bounding_box.longitude_from <= user.longitude <= bounding_box.longitude_to

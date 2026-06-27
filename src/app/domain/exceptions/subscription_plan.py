from app.domain.exceptions.base import DomainException


class SubscriptionPlanException(DomainException):
  """Clase base para las excepciones relacionadas con la suscripción a planes."""
  pass

class SubscriptionPlanNotFoundError(SubscriptionPlanException):
  """Excepción lanzada cuando no se encuentra una suscripción a un plan."""
  pass

class SubscriptionPlanAlreadyExistsError(SubscriptionPlanException):
  """Excepción lanzada cuando ya existe una suscripción a un plan."""
  pass

class SubscriptionPlanInvalidDataError(SubscriptionPlanException):
  """Excepción lanzada cuando los datos de la suscripción a un plan son inválidos."""
  pass

class SubscriptionPlanLimitExceededError(SubscriptionPlanException):
  """Excepción lanzada cuando se excede el límite de suscripciones a un plan."""
  pass

class SubscriptionPlanPaymentFailedError(SubscriptionPlanException):
  """Excepción lanzada cuando falla el pago de la suscripción a un plan."""
  pass

class SubscriptionPlanHasActiveSubscriptionsError(SubscriptionPlanException):
  """Excepción lanzada al intentar eliminar un plan que tiene empresas suscritas."""
  pass
